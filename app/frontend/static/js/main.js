document.addEventListener("DOMContentLoaded", function () {
    const generateBtn = document.getElementById("generate-btn");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    generateBtn.addEventListener("click", function () {
        const stack = document.getElementById("stack").value.trim();
        const description = document.getElementById("description").value.trim();

        if (!stack || !description) {
            alert("Please enter both stack and description!");
            return;
        }

        loading.classList.remove("hidden");
        result.classList.add("hidden");

        fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ stack, description })
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add("hidden");
            if (data.error) {
                result.innerHTML = `<span style="color: red;">❌ ${data.error}</span>`;
            } else {
                result.innerHTML = `<span>✅ Script generated successfully! Stored in <strong>generated_scripts</strong>.</span>`;
            }
            result.classList.remove("hidden");
        })
        .catch(error => {
            loading.classList.add("hidden");
            result.innerHTML = `<span style="color: red;">❌ Failed to generate script.</span>`;
            result.classList.remove("hidden");
        });
    });
});