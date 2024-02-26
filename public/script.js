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

  let factor = (score - minimumScore) / (maximumScore - minimumScore);

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

function formatDate(date) {
  return `${date.getDate().toString().padStart(2, "0")}-${(date.getMonth() + 1)
    .toString()
    .padStart(2, "0")}-${date.getFullYear().toString()}`;
}

function loadGamesForDate(date) {
  const filename = `data/topmatchnba-${formatDate(date)}.json`;

  fetch(filename)
    .then((response) => response.json())
    .then((data) => {
      const container = document.getElementById("games-container");
      container.innerHTML = ""; // Clear existing content
      data.forEach((item) => {
        const game = item.game;
        const homeTeamLogoPath = `nba_logos/${game.home_team.team_name}.png`;
        const visitorTeamLogoPath = `nba_logos/${game.visitor_team.team_name}.png`;
        const color = generateColor(item.game_punctuation);

        const div = document.createElement("div");
        div.className = "game";
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
}

const now = new Date();
const yesterday = new Date(now.setDate(now.getDate() - 1));
let currentDate = yesterday;

const spanCurrentDate = document.createElement("span");
spanCurrentDate.textContent = formatDate(currentDate);

const nextDayButton = document.createElement("button");
nextDayButton.textContent = "Next Day >";
nextDayButton.onclick = function () {
  currentDate.setDate(currentDate.getDate() + 1);
  spanCurrentDate.textContent = formatDate(currentDate);
  console.log(currentDate, "currentDate");
  console.log(now, "now");
  if (currentDate === yesterday) nextDayButton.setAttribute("disabled", true);
  loadGamesForDate(currentDate);
};
if (currentDate === yesterday) nextDayButton.setAttribute("disabled", true);

document.addEventListener("DOMContentLoaded", function () {
  loadGamesForDate(currentDate);
  const container = document.getElementById("controls-container");
  const prevDayButton = document.createElement("button");
  prevDayButton.textContent = "< Previous Day";
  prevDayButton.onclick = function () {
    currentDate.setDate(currentDate.getDate() - 1);
    spanCurrentDate.textContent = formatDate(currentDate);
    nextDayButton.removeAttribute("disabled");
    loadGamesForDate(currentDate);
  };

  container.appendChild(prevDayButton);
  container.appendChild(spanCurrentDate);
  container.appendChild(nextDayButton);
});
