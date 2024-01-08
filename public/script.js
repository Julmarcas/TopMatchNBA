document.addEventListener("DOMContentLoaded", function () {
  fetch("games.json")
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("games-container");
      data.forEach((game) => {
        const div = document.createElement("div");
        div.innerHTML = `<strong>${game.home_team}</strong> vs <strong>${game.visitor_team}</strong> -- ${game.game_punctuation}`;
        container.appendChild(div);
      });
    })
    .catch((error) => console.error("Error:", error));
});
