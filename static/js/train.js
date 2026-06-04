let featureExtractor, classifier, video;
let samples = {};

async function init() {
  featureExtractor = ml5.featureExtractor("MobileNet", modelReady);
  classifier = featureExtractor.classification();

  video = document.getElementById("webcam");
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: "environment" },
  });
  video.srcObject = stream;

  await new Promise((resolve) =>
    video.addEventListener("loadeddata", resolve, { once: true }),
  );
  document.getElementById("status").innerHTML = "Camera ready!";
}

let isModelReady = false;

function modelReady() {
  isModelReady = true;
  document.getElementById("status").innerHTML = "Ready!";
}

function addSample() {
  if (!isModelReady) return alert("Model is still loading, please wait");
  const className = document.getElementById("class-name").value.trim();
  if (!className) return alert("Enter a class name first");

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  classifier.addImage(canvas, className);

  if (!samples[className]) samples[className] = [];
  samples[className].push(canvas.toDataURL("image/jpeg", 0.5));

  const count = samples[className].length;
  document.getElementById("status").innerHTML =
    `"${className}": ${count} sample${count > 1 ? "s" : ""}`;

  renderGallery();
}

async function trainAndSave() {
  const classNames = Object.keys(samples);
  if (classNames.length < 1) return alert("Add at least one class first");

  const minSamples = Math.min(...classNames.map((c) => samples[c].length));
  if (minSamples < 5) return alert("Add at least 5 samples per class");

  document.getElementById("status").innerHTML = "Training...";

  classifier.train(async (lossValue) => {
    if (lossValue !== null) {
      document.getElementById("status").innerHTML =
        `Training... loss: ${lossValue.toFixed(4)}`;
      return;
    }

    // Training complete
    document.getElementById("status").innerHTML = "Saving...";
    const modelData = await classifier.getClassifierData();

    await fetch("/admin/save-class", {
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

    document.getElementById("status").innerHTML = "Saved!";
  });
}

function removeSample(className, index) {
  samples[className].splice(index, 1);
  if (samples[className].length === 0) delete samples[className];

  // Rebuild classifier from remaining samples
  classifier = featureExtractor.classification();
  Object.entries(samples).forEach(([name, images]) => {
    images.forEach((dataUrl) => {
      const img = new Image();
      img.src = dataUrl;
      classifier.addImage(img, name);
    });
  });

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

let savedLat = null;
let savedLon = null;

document.addEventListener("DOMContentLoaded", () => {
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

  init();
});
