// Function to handle star ratings for recipes.
function startRating() {
    // Retrieve each star element by its ID.
    const one = document.getElementById('first');
    const two = document.getElementById('second');
    const three = document.getElementById('third');
    const four = document.getElementById('fourth');
    const five = document.getElementById('fifth');

    // Retrieve the form used for submitting the rating, the CSRF token for secure requests,
    // and the confirmation box element for user interactions.
    const form = document.querySelector('.rate-form');
    const score = document.querySelector('.ratings');
    const confirmBox = document.getElementById('confirm-box');
    const csrf = document.getElementsByName('csrfmiddlewaretoken');

    // Function to handle the visual selection of stars based on user interaction.
    const startRating = (score) => {
        switch (score) {
            case 'first':
                one.classList.add('checked');
                two.classList.remove('checked');
                three.classList.remove('checked');
                four.classList.remove('checked');
                five.classList.remove('checked');
                break;
            case 'second':
                one.classList.add('checked');
                two.classList.add('checked');
                three.classList.remove('checked');
                four.classList.remove('checked');
                five.classList.remove('checked');
                break;
            case 'third':
                one.classList.add('checked');
                two.classList.add('checked');
                three.classList.add('checked');
                four.classList.remove('checked');
                five.classList.remove('checked');
                break;
            case 'fourth':
                one.classList.add('checked');
                two.classList.add('checked');
                three.classList.add('checked');
                four.classList.add('checked');
                five.classList.remove('checked');
                break;
            case 'fifth':
                one.classList.add('checked');
                two.classList.add('checked');
                three.classList.add('checked');
                four.classList.add('checked');
                five.classList.add('checked');
                break;
            default:
                // Default case to clear all checks if score doesn't match any case.
                one.classList.remove('checked');
                two.classList.remove('checked');
                three.classList.remove('checked');
                four.classList.remove('checked');
                five.classList.remove('checked');
        }
    };

    // Function to convert numerical value to a string identifier for the stars.
    const getStringText = (score) => {
        switch (score) {
            case 1:
                return 'first';
            case 2:
                return 'second';
            case 3:
                return 'third';
            case 4:
                return 'fourth';
            case 5:
                return 'fifth';
            default:
                return '0'; // Return '0' for undefined or out-of-bound values.
        }
    };

    // If a pre-existing score exists (not zero), set the stars to reflect the existing rating.
    if (score.id !== '0') {
        const scoreToNumber = Number(score.id);
        const scoreToString = getStringText(scoreToNumber);
        startRating(scoreToString);
    }

    // Function to convert the string identifier back to a numerical value for submission.
    const getNumericValue = (score) => {
        switch (score) {
            case 'first':
                return 1;
            case 'second':
                return 2;
            case 'third':
                return 3;
            case 'fourth':
                return 4;
            case 'fifth':
                return 5;
            default:
                return 0;
        }
    };

    // Add event listeners to each star for user interaction.
    const starsArray = [one, two, three, four, five];
    starsArray.forEach(star => {
        star.addEventListener('click', (event) => {
            const score = event.target.id;
            startRating(score);

            let isSubmitted = false;
            form.addEventListener('submit', e => {
                e.preventDefault();
                if (isSubmitted) return;
                isSubmitted = true;
                // Perform AJAX POST request to submit the rating.
                $.ajax({
                    type: 'POST',
                    url: `/network/recipes/${e.target.id}/rate/`,
                    data: {
                        'csrfmiddlewaretoken': csrf[0].value,
                        'recipe_id': e.target.id,
                        'score': getNumericValue(score),
                    },
                    success: () => {
                        console.log('Rating submitted successfully.')
                        // Fetch the updated part of the page.
                        fetch(window.location.href)
                            .then(response => response.text())
                            .then(html => {
                                const parser = new DOMParser();
                                const doc = parser.parseFromString(html, "text/html");
                                const newRating = doc.querySelector('.average-rating span').textContent;
                                document.querySelector('.average-rating span').textContent = newRating;
                            });
                    },
                    error: error => console.error('Error submitting rating:', error)
                });
            });
        });
    });
}

function handleClick(element) {
    element.classList.toggle('clicked');
}

function toggleDisplay(id) {
    let feedInfo = document.getElementById('feed-info');
    let feedComments = document.getElementById('feed-comments');
    if (id === 'feed-info') {
        feedInfo.style.display = 'block';
        feedComments.style.display = 'none';
    } else if (id === 'feed-comments') {
        feedComments.style.display = 'block';
        feedInfo.style.display = 'none';
    }
}
