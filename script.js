const videoInput = document.getElementById("videoInput");
const chooseBtn = document.getElementById("chooseBtn");
const analyzeBtn = document.getElementById("analyzeBtn");

const fileName = document.getElementById("fileName");

const loading = document.getElementById("loading");
const resultCard = document.getElementById("resultCard");

const prediction = document.getElementById("prediction");

const aiProbability = document.getElementById("aiProbability");
const aiScore = document.getElementById("aiScore");
const realScore = document.getElementById("realScore");

const framesAnalyzed = document.getElementById("framesAnalyzed");
const duration = document.getElementById("duration");
const confidence = document.getElementById("confidence");

const resetBtn = document.getElementById("resetBtn");


/* =====================================================
   CHOOSE VIDEO
===================================================== */

chooseBtn.addEventListener("click", () => {

    videoInput.click();

});


/* =====================================================
   FILE SELECTED
===================================================== */

videoInput.addEventListener("change", () => {

    const file = videoInput.files[0];

    if (!file) {

        fileName.textContent = "No video selected";

        analyzeBtn.disabled = true;

        return;
    }


    fileName.textContent = file.name;

    analyzeBtn.disabled = false;

});


/* =====================================================
   ANALYZE VIDEO
===================================================== */

analyzeBtn.addEventListener("click", async () => {

    const file = videoInput.files[0];


    if (!file) {

        alert("Please select a video first.");

        return;
    }


    /* -----------------------------------------------
       UI
    ------------------------------------------------ */

    analyzeBtn.disabled = true;

    loading.style.display = "block";

    resultCard.style.display = "none";


    /* -----------------------------------------------
       FormData
    ------------------------------------------------ */

    const formData = new FormData();

    formData.append("file", file);


    try {

        /* -------------------------------------------
           Send video to FastAPI
        -------------------------------------------- */

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",
                body: formData
            }
        );


        /* -------------------------------------------
           Check HTTP response
        -------------------------------------------- */

       if (!response.ok) {
    let errorMessage = `Server error: ${response.status}`;

    try {
        const errorData = await response.json();

        if (errorData.detail) {
            errorMessage = errorData.detail;
        }

        if (errorData.message) {
            errorMessage = errorData.message;
        }

    } catch (e) {
        // Response wasn't JSON
    }

    throw new Error(errorMessage);
}


        const data = await response.json();


        /* -------------------------------------------
           Check backend response
        -------------------------------------------- */

        if (!data.success) {

            throw new Error(
                data.message || "Video analysis failed."
            );

        }


        /* -------------------------------------------
           Display prediction
        -------------------------------------------- */

        prediction.textContent =
            data.prediction;


        /* -------------------------------------------
           Display scores
        -------------------------------------------- */

        aiProbability.textContent =
            data.ai_probability;

        aiScore.textContent =
            `${data.ai_probability}%`;

        realScore.textContent =
            `${data.real_probability}%`;


        /* -------------------------------------------
           Display details
        -------------------------------------------- */

        framesAnalyzed.textContent =
            data.analyzed_frames;

        duration.textContent =
            `${data.duration} sec`;

        confidence.textContent =
            `${data.confidence}%`;


        /* -------------------------------------------
           Show result
        -------------------------------------------- */

        resultCard.style.display = "block";


        /* -------------------------------------------
           Scroll to result
        -------------------------------------------- */

        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });


    } catch (error) {

        console.error(error);

        alert(
            "Could not analyze the video.\n\n" +
            error.message
        );

    } finally {

        loading.style.display = "none";

        analyzeBtn.disabled = false;

    }

});


/* =====================================================
   RESET
===================================================== */

resetBtn.addEventListener("click", () => {

    videoInput.value = "";

    fileName.textContent =
        "No video selected";

    analyzeBtn.disabled = true;

    resultCard.style.display = "none";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

});