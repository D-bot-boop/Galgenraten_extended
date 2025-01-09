// Funktion: Neues Wort starten
function startNewWord() {
    fetch('/start_game', {
        method: 'POST'
    }).then(response => response.json())
    .then(data => {
        if (data.word) {
            // Spielstatus zurücksetzen
            document.getElementById('word-display').textContent = data.word;
            document.getElementById('wrong-letters').textContent = '';
            document.getElementById('message').textContent = '';
            document.getElementById('hangman-image').src = '/static/images/0.png';
            document.getElementById('difficulty-display').textContent = `Schwierigkeit: ${data.difficulty}`;
            document.getElementById('mmr-display').textContent = `MMR: ${data.mmr}`;
            document.getElementById('rank-display').textContent = `Rang: ${data.rank}`;
            document.getElementById("coins-display").textContent = `Münzen: ${data.coins.toFixed(1)} ◎`;
            document.getElementById('winstreak-display').textContent = `Winstreak: ${data.winstreak}`;
            document.getElementById('guess').disabled = false; // Eingabe aktivieren
        } else {
            document.getElementById('message').textContent = data.error || 'Fehler beim Laden eines neuen Wortes.';
        }
    });
}

// Funktion: Spielstatus abrufen
function fetchGameState() {
    fetch('/game_state', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            console.log("[DEBUG] Spielstatus:", data);

            if (data.error) {
                document.getElementById('message').textContent = data.error;
                document.getElementById('guess').disabled = true; // Eingabe blockieren
            } else {
                // Spielstatus aktualisieren
                document.getElementById('word-display').textContent = data.word_display || '';
                document.getElementById('wrong-letters').textContent = data.wrong_letters?.join(', ') || '';
                document.getElementById('mmr-display').textContent = `MMR: ${data.mmr}`;
                document.getElementById('rank-display').textContent = `Rang: ${data.rank}`;
                document.getElementById('winstreak-display').textContent = `Winstreak: ${data.winstreak}`;
                document.getElementById("coins-display").textContent = `Münzen: ${data.coins.toFixed(1)} ◎`;
                document.getElementById('difficulty-display').textContent = `Schwierigkeit: ${data.difficulty}`;
                document.getElementById('hangman-image').src = data.image_path || '/static/images/default.png';
            }
        })
        .catch(error => {
            console.error("[DEBUG] Fehler beim Abrufen des Spielstatus:", error);
            document.getElementById('message').textContent = "Ein Fehler ist aufgetreten.";
        });
}

// Funktion: Buchstaben raten
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
        .then(response => response.json())
        .then(data => {
            console.log("[DEBUG] Antwort von /guess_letter:", data);

            if (data.error) {
                document.getElementById("message").textContent = data.error;
                
                if (data.difficulty) {
                    document.getElementById("difficulty-display").textContent = `Schwierigkeit: ${data.difficulty}`;
                }
            
            } else if (data.game_over) {
                    document.getElementById("message").textContent = data.message;
                    document.getElementById("guess").disabled = true; // Eingabe blockieren
                    document.getElementById("hangman-image").src = data.image_path || '/static/images/default.png';
                    document.getElementById("word-display").textContent = data.word_display;
                    document.getElementById('rank-display').textContent = `Rang: ${data.rank}`; 
                    // Aktualisiere MMR, Rang, Winstreak und Münzen
                    document.getElementById("mmr-display").textContent = `MMR: ${data.mmr}`;
                    document.getElementById("rank-display").textContent = `Rang: ${data.rank}`;
                    document.getElementById("winstreak-display").textContent = `Winstreak: ${data.winstreak}`;
                    document.getElementById("coins-display").textContent = `Münzen: ${data.coins.toFixed(1)} ◎`;
                
                    // Zeige verdiente oder verlorene Münzen in der Nachricht
                    if (data.coins_earned) {
                        document.getElementById("message").textContent += ` Du hast ${data.coins_earned} ◎ verdient!`;
                    } else if (data.coins_penalty) {
                        document.getElementById("message").textContent += ` Du hast ${data.coins_penalty} ◎ verloren.`;
                    }
                
                    console.log(`[DEBUG] Spiel vorbei. MMR: ${data.mmr}, Rang: ${data.rank}, Winstreak: ${data.winstreak}, Münzen: ${data.coins}`);
            } else {
                // Normaler Spielstatus
                document.getElementById("word-display").textContent = data.word_display;
                document.getElementById("wrong-letters").textContent = data.wrong_letters.join(", ");
                document.getElementById("message").textContent = data.message;
                document.getElementById("hangman-image").src = data.image_path || '/static/images/default.png';
                console.log(`[DEBUG] Bild aktualisiert auf: ${data.image_path}`);
            }

            // Schwierigkeit in Sternen aktualisieren (falls vorhanden)
            document.getElementById("difficulty-display").textContent = `Schwierigkeit: ${data.difficulty || 'Unbekannt'}`;
        })
        .catch(error => {
            console.error("[DEBUG] Fehler beim Raten eines Buchstabens:", error);
            document.getElementById("message").textContent = "Ein Fehler ist aufgetreten.";
        });

    letterInput.value = "";
}

// Funktion: Leaderboard laden
function loadLeaderboard() {
    fetch('/leaderboard/json', { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP-Fehler: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const leaderboard = document.getElementById('leaderboard');
            leaderboard.innerHTML = ''; // Aktuelle Inhalte entfernen

            if (data.length === 0) {
                leaderboard.innerHTML = '<li class="list-group-item">Keine Spieler gefunden.</li>';
                return;
            }

            data.forEach(player => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.textContent = `${player.username} - ${player.mmr} MMR - ${player.rank}`;
                leaderboard.appendChild(listItem);
            });
        })
        .catch(error => {
            console.error("Fehler beim Laden des Leaderboards:", error);
            const leaderboard = document.getElementById('leaderboard');
            leaderboard.innerHTML = '<li class="list-group-item text-danger">Fehler beim Laden der Daten. Überprüfe die Serverantwort.</li>';
        });
}


function buyHint() {
    fetch('/reveal_letter', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("message").textContent = data.error;
        } else {
            // Aktualisiere das Anzeige-Wort und die Münzen
            document.getElementById("word-display").textContent = data.word;
            document.getElementById("coins-display").textContent = `Münzen: ${data.coins.toFixed(1)} ◎`;
            document.getElementById("message").textContent = data.message;

            console.log(`[DEBUG] Buchstabe aufgedeckt: ${data.message}`);
        }
    })
    .catch(error => {
        console.error("[DEBUG] Fehler beim Kauf eines Tipps:", error);
        document.getElementById("message").textContent = "Ein Fehler ist aufgetreten.";
    });
}


// Event Listener hinzufügen: Enter-Taste aktiviert "Rate den Buchstaben"
document.addEventListener('DOMContentLoaded', () => {
    loadLeaderboard();
    fetchGameState();

    const guessInput = document.getElementById("guess");
    guessInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            makeGuess(); // Buchstaben raten
        }
    });
});