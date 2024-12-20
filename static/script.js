async function makeGuess() {
    const letter = document.getElementById('letter').value;
    const response = await fetch('/guess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ letter }),
    });
    const data = await response.json();
    document.getElementById('message').innerText = data.message;
}
