function interpolarColor(color1, color2, factor) {
  if (arguments.length < 3) {
    factor = 0.5;
  }
  var result = color1.slice();
  for (var i = 0; i < 3; i++) {
    result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
  }
  return result;
}

// function rgbAHex(rgb) {
//   return "#" + rgb.map(function(value) {
//     return ("0" + value.toString(16)).slice(-2);
//   }).join('');
// }

function colorAStringRGBA(color) {
  return `rgba(${color[0]}, ${color[1]}, ${color[2]})`;
}

function generarColor(puntuacion) {
  const verde = [0, 255, 0];
  const amarillo = [255, 255, 0];
  const naranja = [255, 165, 0];
  const rojo = [255, 0, 0];
  const puntuacionMaxima = 30;
  const puntuacionMinima = 0;

  let factor =
    (puntuacion - puntuacionMinima) / (puntuacionMaxima - puntuacionMinima);

  // Decide el color base y el factor de interpolación basado en el rango de puntuación
  if (factor > 0.75) {
    return colorAStringRGBA(
      interpolarColor(verde, amarillo, (factor - 0.75) * 4),
    );
  } else if (factor > 0.5) {
    return colorAStringRGBA(
      interpolarColor(amarillo, naranja, (factor - 0.5) * 4),
    );
  } else if (factor > 0.25) {
    return colorAStringRGBA(
      interpolarColor(naranja, rojo, (factor - 0.25) * 4),
    );
  } else {
    return colorAStringRGBA(rojo);
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
        const color = generarColor(item.game_punctuation);

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
