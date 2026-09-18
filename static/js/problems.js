let selectedProblemId = null;


// ---------------------------------------------------------
// SHOW DETAILS
// ---------------------------------------------------------

function showDetails(code, title, description) {

    document.getElementById("modalCode").textContent = code;

    document.getElementById("modalTitle").textContent = title;

    document.getElementById("modalDescription").textContent =
        description;

    document
        .getElementById("detailsModal")
        .classList.add("active");
}


function closeDetails() {

    document
        .getElementById("detailsModal")
        .classList.remove("active");
}


// ---------------------------------------------------------
// CONFIRMATION
// ---------------------------------------------------------

function selectProblem(problemId) {

    const button =
        document.getElementById(
            `select-${problemId}`
        );

    if (button.disabled) {
        return;
    }

    selectedProblemId = problemId;

    document
        .getElementById("confirmModal")
        .classList.add("active");


    document.getElementById(
        "confirmButton"
    ).onclick = function () {

        submitSelection(problemId);

    };
}


function closeConfirm() {

    document
        .getElementById("confirmModal")
        .classList.remove("active");
}


// ---------------------------------------------------------
// SUBMIT
// ---------------------------------------------------------

async function submitSelection(problemId) {

    const confirmButton =
        document.getElementById(
            "confirmButton"
        );

    confirmButton.disabled = true;

    confirmButton.textContent =
        "Selecting...";


    const formData = new FormData();

    formData.append(
        "problem_id",
        problemId
    );


    try {

        const response = await fetch(
            "/select-problem",
            {
                method: "POST",
                body: formData
            }
        );


        const data = await response.json();


        if (data.success) {

            window.location.href =
                data.redirect;

        } else {

            closeConfirm();

            alert(data.message);

            loadProblemStatus();

        }

    } catch (error) {

        closeConfirm();

        alert(
            "Unable to connect to the server. Please try again."
        );

    } finally {

        confirmButton.disabled = false;

        confirmButton.textContent =
            "Confirm Selection";
    }
}


// ---------------------------------------------------------
// LIVE STATUS
// ---------------------------------------------------------

async function loadProblemStatus() {

    try {

        const response = await fetch(
            "/api/problems"
        );

        if (!response.ok) {
            return;
        }

        const problems =
            await response.json();


        problems.forEach(problem => {

            const count =
                document.getElementById(
                    `count-${problem.id}`
                );

            const button =
                document.getElementById(
                    `select-${problem.id}`
                );

            const card =
                document.getElementById(
                    `problem-${problem.id}`
                );


            if (!count || !button || !card) {
                return;
            }


            count.textContent =
                `${problem.selected_count} / 2`;


            if (problem.locked) {

                button.disabled = true;

                button.textContent =
                    "🔒 Locked";

                card.classList.add(
                    "is-locked"
                );

            } else {

                button.disabled = false;

                button.innerHTML =
                    'Select Problem <span>→</span>';

                card.classList.remove(
                    "is-locked"
                );

            }

        });

    } catch (error) {

        console.log(
            "Status update failed."
        );

    }
}


// ---------------------------------------------------------
// AUTO UPDATE EVERY 2 SECONDS
// ---------------------------------------------------------

setInterval(
    loadProblemStatus,
    2000
);


// First load
loadProblemStatus();


// ---------------------------------------------------------
// CLOSE MODALS WHEN CLICKING OUTSIDE
// ---------------------------------------------------------

document.addEventListener(
    "click",
    function(event) {

        const detailsModal =
            document.getElementById(
                "detailsModal"
            );

        const confirmModal =
            document.getElementById(
                "confirmModal"
            );


        if (
            event.target === detailsModal
        ) {

            closeDetails();

        }


        if (
            event.target === confirmModal
        ) {

            closeConfirm();

        }

    }
);