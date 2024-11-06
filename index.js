document.getElementById('playlist-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    
    // Get the playlist URL from the form
    const playlistUrl = document.getElementById('playlist').value;

    // Make a GET request to the backend with the playlist URL as a query parameter
  const response = await fetch(`http://127.0.0.1:5000/get_music?playlist=${encodeURIComponent(playlistUrl)}`, {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    }
});


    const data = await response.json();
    console.log(data);


    // Populate the music list checkboxes
    const musicListDiv = document.getElementById('music-list');
    musicListDiv.innerHTML = '';  // Clear previous content
    data.forEach((song, index) => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.classList.add('song-checkbox');
        checkbox.name = `${song.track_name}`;
        checkbox.value = song["track_uri"];
        checkbox.id = `song-${index}`;

        const label = document.createElement('label');
        label.htmlFor = `song-${index}`;
        label.textContent = `${song.track_name} by ${song.artist_name}`;

        const br = document.createElement('br');

        musicListDiv.appendChild(checkbox);
        musicListDiv.appendChild(label);
        musicListDiv.appendChild(br);
    });
});

document.getElementById('select-all').addEventListener('click', function () {
    const checkboxes = document.querySelectorAll('#music-list input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = true);
});

document.getElementById('deselect-all').addEventListener('click', function () {
    const checkboxes = document.querySelectorAll('#music-list input[type="checkbox"]');
    checkboxes.forEach(checkbox => checkbox.checked = false);
});


document.getElementById('download-selected').addEventListener('click', async function () {
    event.preventDefault();
    const checkboxes=document.querySelectorAll('#music-list input[type="checkbox"]');
    const selectedCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.checked);
    const selectedSongs = selectedCheckboxes.map(checkbox => checkbox.name);
    console.log(selectedSongs);
    console.log(selectedCheckboxes);
    checkboxes.forEach(checkbox => checkbox.checked = false);
    for (const song of selectedSongs) {
         

        const response = await fetch('http://127.0.0.1:5000/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ song: song })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${song}.mp3`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            console.log(blob);
            console.log("mediafile");
        });
    }


});