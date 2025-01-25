
// Funktion: Statistik laden (dynamisch bei Hover)
//function loadStatsOnHover() {
 //   const statsContainer = document.querySelector(".stats-container");

//    statsContainer.addEventListener("mouseover", () => {
//        fetch('/get_stats', { method: 'GET' })
//            .then(response => response.json())
//           .then(data => {
//                // Aktualisiere die Statistik-Daten
//                document.getElementById('stats-wins').textContent = `Gewonnene Spiele: ${data.wins}`;
//                document.getElementById('stats-losses').textContent = `Verlorene Spiele: ${data.losses}`;
//                document.getElementById('stats-winrate').textContent = `Gewinnwahrscheinlichkeit: ${data.winrate}%`;
//               document.getElementById('stats-highest-winstreak').textContent = `Höchste Winstreak: ${data.highest_winstreak}`;
//                document.getElementById('stats-highest-mmr').textContent = `Höchste MMR: ${data.highest_mmr}`;
//           })
//            .catch(error => {
//                console.error('Fehler beim Laden der Statistik:', error);
//            });
//    });
//}

// Funktion: Statistik einmal beim Laden aktualisieren
document.addEventListener('DOMContentLoaded', () => {
    loadStatsOnHover();
});


// Funktion: Neues Wort starten
function startNewWord() {
    fetch('/start_game', {
        method: 'POST'
    })
    .then(response => response.json())
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

            // Beschreibung zurücksetzen
            document.getElementById('description-container').style.display = 'none';
            document.getElementById('description-text').textContent = '';

            document.getElementById("guess").focus();

            // Statistik aktualisieren
            loadStats();
        } else {
            document.getElementById('message').textContent = data.error || 'Fehler beim Laden eines neuen Wortes.';
        }
    }).catch(error => {
        console.error("Fehler beim Starten eines neuen Spiels:", error);
        document.getElementById('message').textContent = "Tippe Buchstaben zum Raten ein";
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
            document.getElementById('message').textContent = "Beginne ein Spiel indem du einen Buchstaben rätst.";
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
            document.getElementById("message").textContent = "Ein Fehler ist aufgetreten3.";
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

function changeLanguage() {
    const languageSelect = document.getElementById("language");
    const selectedLanguage = languageSelect.value;

    fetch('/change_language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: selectedLanguage })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Fehler: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error("Fehler beim Ändern der Sprache:", data.error);
            alert(data.error); // Benutzer informieren
        } else {
            console.log("Sprache erfolgreich geändert:", data.message);
            alert(data.message); // Benutzer informieren
        }
    })
    .catch(error => {
        console.error("Fehler beim Ändern der Sprache:", error);
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

            document.getElementById("guess").focus();
        }
    })
    .catch(error => {
        console.error("[DEBUG] Fehler beim Kauf eines Tipps:", error);
        document.getElementById("message").textContent = "Ein Fehler ist aufgetreten4.";
    });
}


function getDescription() {
    fetch('/describe_word', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("message").textContent = data.error;
        } else {
            // Aktualisiere die Beschreibung und die Münzenanzeige
            document.getElementById("description-text").textContent = data.description;

            // Zeige den Container mit Animation
            const descriptionContainer = document.getElementById("description-container");
            descriptionContainer.style.display = 'block'; // Sichtbar machen
            descriptionContainer.classList.add("show"); // Animation hinzufügen

            // Münzenanzeige aktualisieren
            document.getElementById("coins-display").textContent = `Münzen: ${data.coins.toFixed(1)} ◎`;
            document.getElementById("message").textContent = "Ein Tipp wurde erfolgreich genutzt!";
            
            console.log(`[DEBUG] Beschreibung erhalten: ${data.description}`);

            document.getElementById("guess").focus();
        }
    })
    .catch(error => {
        console.error("[DEBUG] Fehler beim Abrufen der Beschreibung:", error);
        document.getElementById("message").textContent = "Ein Fehler ist aufgetreten5.";
    });
}



// Event Listener hinzufügen: Enter-Taste und Hotkeys
document.addEventListener('DOMContentLoaded', () => {
    loadLeaderboard();
    fetchGameState();

    const guessInput = document.getElementById("guess");
    guessInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            makeGuess(); // Buchstaben raten
        }
    });

    
    // Hotkeys hinzufügen
    document.addEventListener("keydown", (event) => {
        switch (event.key) {
            case "1": // Hotkey 1: Buchstabe aufdecken
                buyHint();
                break;
            case "2": // Hotkey 2: Umschreibung anfordern
                getDescription();
                break;
            case "3": // Hotkey 3: Neues Spiel starten
                startNewWord();
                break;
            case "4": // Hotkey 4: Zur Startseite zurückkehren
                window.location.href = "/"; // URL zur Startseite
                break;
            default:
                // Andere Tasten ignorieren
                break;
        }
    });
});
