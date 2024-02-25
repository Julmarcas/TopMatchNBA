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
      data.forEach((item) => {
        const game = item.game;
        const homeTeamLogoPath = `nba_logos/${game.home_team.team_name}.png`;
        const visitorTeamLogoPath = `nba_logos/${game.visitor_team.team_name}.png`;

        const div = document.createElement("div");
        div.className = "game";

        div.innerHTML = `
  <div class="team">
    <img src="${homeTeamLogoPath}" alt="${game.home_team.team_name}" title="${game.home_team.team_name}" />
  </div>
  <span>vs</span>
  <div class="team">
    <img src="${visitorTeamLogoPath}" alt="${game.visitor_team.team_name}" title="${game.visitor_team.team_name}" />
  </div>
  <div class="game_punctuation">-- Points: ${item.game_punctuation}</div>
`;

        container.appendChild(div);
      });
    })
    .catch((error) => console.error("Error:", error));
});
