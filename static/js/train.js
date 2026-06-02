let model, webcam;
let samples = {}; // { className: [imageDataUrl, ...] }

async function init() {
  // Start webcam
  webcam = new tmImage.Webcam(300, 300, false);
  await webcam.setup({ facingMode: "environment" });
  await webcam.play();

  document.getElementById("webcam-container").appendChild(webcam.canvas);
  document.getElementById("loading-spinner").classList.add("d-none");
  document.getElementById("status").innerHTML = "Ready!";

  window.requestAnimationFrame(loop);
}

function loop() {
  webcam.update();
  window.requestAnimationFrame(loop);
}

function addSample() {
  const className = document.getElementById("class-name").value.trim();
  if (!className) return alert("Enter a class name first");

  // Grab current frame
  const canvas = document.createElement("canvas");
  canvas.width = webcam.canvas.width;
  canvas.height = webcam.canvas.height;
  canvas.getContext("2d").drawImage(webcam.canvas, 0, 0);

  // Store it
  if (!samples[className]) samples[className] = [];
  samples[className].push(canvas.toDataURL("image/jpeg", 0.5));

  const count = samples[className].length;
  document.getElementById("status").innerHTML =
    `"${className}": ${count} sample${count > 1 ? "s" : ""}`;

  renderGallery();
}

async function trainAndSave() {
  const classNames = Object.keys(samples);
  if (classNames.length < 2) return alert("You need at least 2 classes");

  const minSamples = Math.min(...classNames.map((c) => samples[c].length));
  if (minSamples < 5) return alert("Add at least 5 samples per class");

  document.getElementById("status").innerHTML = "Training...";

  // Build the model
  model = await tmImage.createTeachable(
    { tfjsVersion: tf.version.tfjs },
    { version: 2, alpha: 0.35 },
  );

  await model.prepareDataset();

  // Load samples into the model
  for (const className of classNames) {
    const classIndex = classNames.indexOf(className);
    await model.addClassifier(classIndex, className);

    for (const dataUrl of samples[className]) {
      const img = new Image();
      img.src = dataUrl;
      await new Promise((r) => (img.onload = r));
      await model.addExample(classIndex, img);
    }
  }

  // Train
  await model.train(
    { denseUnits: 100, epochs: 50, learningRate: 0.001, batchSize: 16 },
    {
      onEpochEnd: (epoch, logs) => {
        document.getElementById("status").innerHTML =
          `Training... epoch ${epoch + 1}/50`;
      },
    },
  );

  document.getElementById("status").innerHTML = "Saving...";

  // Export and send to Flask
  const savedModel = await model.save(
    tf.io.withSaveHandler(async (artifacts) => {
      const modelData = {
        modelTopology: artifacts.modelTopology,
        weightSpecs: artifacts.weightSpecs,
        weightData: Array.from(new Uint8Array(artifacts.weightData)),
        labels: classNames,
      };

      await fetch("/admin/save-classifier", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(modelData),
      });

      document.getElementById("status").innerHTML = "Saved!";
      let savedLat = null;
      let savedLon = null;

      document
        .getElementById("flexCheckDefault")
        .addEventListener("change", function () {
          if (this.checked) {
            navigator.geolocation.getCurrentPosition(
              (position) => {
                savedLat = position.coords.latitude;
                savedLon = position.coords.longitude;
                document.getElementById("location").innerHTML +=
                  ` <small class="text-success">(${savedLat.toFixed(4)}, ${savedLon.toFixed(4)})</small>`;
              },
              () => {
                this.checked = false;
                alert("Could not get location — check browser permissions");
              },
            );
          } else {
            savedLat = null;
            savedLon = null;
          }
        });
      await fetch("/admin/save-classifier", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...modelData,
          class_name: document.getElementById("confirm-class-name").value,
          location: document.getElementById("flexCheckDefault").checked,
          lat: savedLat,
          lon: savedLon,
        }),
      });
      return { modelArtifactsInfo: {} };
    }),
  );
}

function removeSample(className, index) {
  samples[className].splice(index, 1);
  if (samples[className].length === 0) delete samples[className];
  renderGallery();
}

function renderGallery() {
  const gallery = document.getElementById("sample-gallery");
  gallery.innerHTML = Object.entries(samples)
    .map(
      ([className, images]) => `
    <div>
      <strong>${className} (${images.length})</strong>
      <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
        ${images
          .map(
            (src, i) => `
          <div style="position: relative;">
            <img src="${src}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;"/>
            <button onclick="removeSample('${className}', ${i})" style="
              position: absolute; top: 2px; right: 2px;
              background: red; color: white; border: none;
              border-radius: 50%; width: 20px; height: 20px;
              cursor: pointer; font-size: 12px;
            ">×</button>
          </div>
        `,
          )
          .join("")}
      </div>
    </div>
  `,
    )
    .join("");
}

window.addEventListener("load", init);
