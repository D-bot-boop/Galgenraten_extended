async function makeGuess() {
    const letter = document.getElementById('letter').value;
    const response = await fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ letter }),
    });
    const data = await response.json();
    document.getElementById('message').innerText = data.message;

    // Aktualisieren des Spielstatus nach einem Rateversuch
    fetch('/game_state', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('word-display').textContent = data.word_display;
            document.getElementById('mmr-display').textContent = `MMR: ${data.mmr}`;
            document.getElementById('rank-display').textContent = `Rang: ${data.rank}`;
        });
}
