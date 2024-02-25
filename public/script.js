document.addEventListener("DOMContentLoaded", function () {
  const now = new Date();
  const yesterday = new Date(now.setDate(now.getDate() - 1));
  const yesterday_date = `${yesterday.getDate().toString().padStart(2, "0")}-${(
    yesterday.getMonth() + 1
  )
    .toString()
    .padStart(2, "0")}-${yesterday.getFullYear().toString()}`;

  const filename = `data/topmatchnba-${yesterday_date}.json`;

  fetch(filename)
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
