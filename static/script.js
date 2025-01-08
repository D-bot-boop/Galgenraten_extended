function startNewWord() {
    fetch('/start_game', {
        method: 'POST'
    }).then(response => response.json())
    .then(data => {
        if (data.word) {
            document.getElementById('word-display').textContent = data.word;
            document.getElementById('wrong-letters').textContent = '';
            document.getElementById('message').textContent = '';
            document.getElementById('hangman-image').src = '/static/images/0.png';
            document.getElementById('difficulty-display').textContent = `Schwierigkeit: ${data.difficulty}`;
            document.getElementById('guess').disabled = false; // Eingabe aktivieren
        } else {
            document.getElementById('message').textContent = data.error || 'Fehler beim Laden eines neuen Wortes.';
        }
    });
}

function fetchGameState() {
    fetch('/game_state', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('message').textContent = data.error;
                document.getElementById('guess').disabled = true; // Eingabe blockieren
            } else {
                document.getElementById('word-display').textContent = data.word_display || '';
                document.getElementById('wrong-letters').textContent = data.wrong_letters?.join(', ') || '';
                document.getElementById('mmr-display').textContent = `MMR: ${data.mmr}`;
                document.getElementById('rank-display').textContent = `Rang: ${data.rank}`;
                document.getElementById('winstreak-display').textContent = `Winstreak: ${data.winstreak}`;
                document.getElementById('difficulty-display').textContent = `Schwierigkeit: ${data.difficulty}`;

                const hangmanImage = document.getElementById('hangman-image');
                hangmanImage.src = data.image_path || '/static/images/default.png';
            }
        })
        .catch(error => {
            console.error("Fehler:", error);
            document.getElementById('message').textContent = "Ein Fehler ist aufgetreten.";
        });
}


function makeGuess() {
    const letterInput = document.getElementById("guess");
    const letter = letterInput.value.trim().toLowerCase();

    if (!letter || letter.length !== 1) {
        document.getElementById("message").textContent = "Bitte einen gültigen Buchstaben eingeben.";
        return;
    }

    fetch("/guess_letter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ letter }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.game_over) {
                document.getElementById("message").textContent = data.message;
                document.getElementById("guess").disabled = true; // Eingabe blockieren
            } else {
                document.getElementById("word-display").textContent = data.word_display;
                document.getElementById("wrong-letters").textContent = data.wrong_letters.join(", ");
                document.getElementById("message").textContent = data.message;
            }
        })
        .catch(error => {
            console.error("Fehler:", error);
            document.getElementById("message").textContent = "Ein Fehler ist aufgetreten.";
        });

    letterInput.value = "";
}


// Lade Spielstatus beim Seitenladen
document.addEventListener('DOMContentLoaded', () => {
    fetchGameState();
});