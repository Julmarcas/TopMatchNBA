function interpolateColor(color1, color2, factor) {
  if (arguments.length < 3) {
    factor = 0.5;
  }
  var result = color1.slice();
  for (var i = 0; i < 3; i++) {
    result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
  }
  return result;
}

function colorToRGBAString(color) {
  return `rgba(${color[0]}, ${color[1]}, ${color[2]})`;
}

function generateColor(score) {
  const green = [0, 255, 0];
  const yellow = [255, 255, 0];
  const orange = [255, 165, 0];
  const red = [255, 0, 0];
  const maximumScore = 18;
  const minimumScore = 0;

  let factor =
    (score - minimumScore) / (maximumScore - minimumScore);

  // Decide the base color and interpolation factor based on the score range
  if (factor > 0.75) {
    return colorToRGBAString(
      interpolateColor(green, yellow, (factor - 0.75) * 4),
    );
  } else if (factor > 0.5) {
    return colorToRGBAString(
      interpolateColor(yellow, orange, (factor - 0.5) * 4),
    );
  } else if (factor > 0.25) {
    return colorToRGBAString(
      interpolateColor(orange, red, (factor - 0.25) * 4),
    );
  } else {
    return colorToRGBAString(red);
  }
}

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
        const color = generateColor(item.game_punctuation);

        const div = document.createElement("div");
        div.className = "game";
        // div.style.backgroundColor = color;
        div.innerHTML = `
  <div class="team">
    <img src="${homeTeamLogoPath}" alt="${game.home_team.team_name}" title="${game.home_team.team_name}" />
  <span>vs</span>
    <img src="${visitorTeamLogoPath}" alt="${game.visitor_team.team_name}" title="${game.visitor_team.team_name}" />
  </div>
  <div class="game_punctuation" style="color:${color}">${item.game_punctuation}</div>
`;

        container.appendChild(div);
      });
    })
    .catch((error) => console.error("Error:", error));
});
