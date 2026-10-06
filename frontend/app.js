const $ = (id) => document.getElementById(id);

const stateSelect = $("state");
const districtSelect = $("district");
const yearSelect = $("year");
const areaInput = $("area");
const form = $("predictionForm");

const weatherState = $("weatherState");
const weatherDistrict = $("weatherDistrict");

const insightsState = $("insightsState");
const insightsDistrict = $("insightsDistrict");

function showError(target, message) {
  target.textContent = message;
  target.className = "message";
}

function clearError(target) {
  target.textContent = "";
  target.className = "message hidden";
}

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error();

    $("apiStatus").classList.add("online");
    $("apiStatus").classList.remove("offline");
    $("apiStatus").querySelector("strong").textContent = "Online";
  } catch {
    $("apiStatus").classList.add("offline");
    $("apiStatus").classList.remove("online");
    $("apiStatus").querySelector("strong").textContent = "Offline";
  }
}

function populateYears() {
  for (let year = 2015; year >= 1997; year--) {
    const option = document.createElement("option");
    option.value = year;
    option.textContent = year;
    yearSelect.appendChild(option);
  }
}

async function getStates() {
  const response = await fetch("/states");
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to load states.");
  }

  return data.states;
}

function fillStates(select, states) {
  select.innerHTML = '<option value="">Select state</option>';

  for (const state of states) {
    const option = document.createElement("option");
    option.value = state;
    option.textContent = state;
    select.appendChild(option);
  }
}

async function getDistricts(state) {
  const response = await fetch(`/districts/${encodeURIComponent(state)}`);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Unable to load districts.");
  }

  return data.districts;
}

async function fillDistricts(select, state) {
  select.disabled = true;
  select.innerHTML = '<option value="">Loading...</option>';

  if (!state) {
    select.innerHTML = '<option value="">Select district</option>';
    return;
  }

  const districts = await getDistricts(state);

  select.innerHTML = '<option value="">Select district</option>';

  for (const district of districts) {
    const option = document.createElement("option");
    option.value = district;
    option.textContent = district;
    select.appendChild(option);
  }

  select.disabled = false;
}

async function initializeLocations() {
  try {
    const states = await getStates();

    fillStates(stateSelect, states);
    fillStates(weatherState, states);
    fillStates(insightsState, states);
  } catch (error) {
    showError($("formMessage"), error.message);
  }
}

stateSelect.addEventListener("change", async () => {
  clearError($("formMessage"));

  try {
    await fillDistricts(districtSelect, stateSelect.value);
  } catch (error) {
    showError($("formMessage"), error.message);
  }
});

weatherState.addEventListener("change", async () => {
  clearError($("weatherMessage"));

  try {
    await fillDistricts(weatherDistrict, weatherState.value);
  } catch (error) {
    showError($("weatherMessage"), error.message);
  }
});

insightsState.addEventListener("change", async () => {
  clearError($("insightsMessage"));

  try {
    await fillDistricts(insightsDistrict, insightsState.value);
  } catch (error) {
    showError($("insightsMessage"), error.message);
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError($("formMessage"));

  const payload = {
    state: stateSelect.value,
    district: districtSelect.value,
    year: Number(yearSelect.value),
    area: Number(areaInput.value)
  };

  if (!payload.state || !payload.district || !payload.year || !payload.area) {
    showError($("formMessage"), "Complete all required fields.");
    return;
  }

  $("predictButton").disabled = true;
  $("buttonText").textContent = "Running model...";
  $("outputState").textContent = "PROCESSING";

  try {
    const response = await fetch("/predict-yield", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Prediction failed.");
    }

    $("yieldValue").textContent =
      Number(data.predicted_yield_tonnes_per_hectare).toFixed(2);

    $("productionValue").textContent =
      Number(data.estimated_production_tonnes).toFixed(2);

    $("resultLocation").textContent =
      `${data.district}, ${data.state}`;

    $("resultYear").textContent = data.year;

    $("resultArea").textContent =
      `${Number(data.area_hectares).toLocaleString()} ha`;

    $("emptyResult").classList.add("hidden");
    $("predictionResult").classList.remove("hidden");
    $("outputState").textContent = "COMPLETE";
  } catch (error) {
    showError($("formMessage"), error.message);
    $("outputState").textContent = "ERROR";
  } finally {
    $("predictButton").disabled = false;
    $("buttonText").textContent = "Run prediction";
  }
});


$("loadWeatherButton").addEventListener("click", async () => {
  clearError($("weatherMessage"));

  const state = weatherState.value;
  const district = weatherDistrict.value;

  if (!state || !district) {
    showError($("weatherMessage"), "Select both state and district.");
    return;
  }

  $("weatherLoadState").textContent = "LOADING";
  $("loadWeatherButton").disabled = true;

  try {
    const response = await fetch(
      `/weather/${encodeURIComponent(state)}/${encodeURIComponent(district)}`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Unable to load weather.");
    }

    const current = data.current || {};
    const advisory = data.irrigation_advisory || {};
    const location = data.location || {};

    $("currentTemp").textContent = current.temperature_2m ?? "—";
    $("currentHumidity").textContent = current.relative_humidity_2m ?? "—";
    $("currentWind").textContent = current.wind_speed_10m ?? "—";
    $("currentRain").textContent = current.precipitation ?? "—";

    $("weatherLocation").textContent =
      `${location.district || district}, ${location.state || state}`;

    $("observedTime").textContent = current.time || "—";

    $("feelsLike").textContent =
      current.apparent_temperature != null
        ? `${current.apparent_temperature} °C`
        : "—";

    $("weatherCode").textContent =
      current.weather_code ?? "—";

    $("weatherSource").textContent =
      data.source || "—";

    $("irrigationLevel").textContent =
      advisory.level || "—";

    $("irrigationMessage").textContent =
      advisory.message || "—";

    $("rain48").textContent =
      advisory.rain_next_48h_mm != null
        ? `${advisory.rain_next_48h_mm} mm`
        : "—";

    $("rainProbability").textContent =
      advisory.today_rain_probability_percent != null
        ? `${advisory.today_rain_probability_percent}%`
        : "—";

    $("et0").textContent =
      advisory.today_reference_et0_mm != null
        ? `${advisory.today_reference_et0_mm} mm`
        : "—";

    const forecastBody = $("forecastBody");
    forecastBody.innerHTML = "";

    for (const day of data.forecast || []) {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${day.date ?? "—"}</td>
        <td>${day.temperature_max_c ?? "—"}</td>
        <td>${day.temperature_min_c ?? "—"}</td>
        <td>${day.precipitation_mm ?? "—"}</td>
        <td>${day.rain_probability_percent ?? "—"}</td>
        <td>${day.reference_et0_mm ?? "—"}</td>
      `;

      forecastBody.appendChild(row);
    }

    $("weatherEmpty").classList.add("hidden");
    $("weatherContent").classList.remove("hidden");
    $("weatherLoadState").textContent = "LIVE";
  } catch (error) {
    showError($("weatherMessage"), error.message);
    $("weatherLoadState").textContent = "ERROR";
  } finally {
    $("loadWeatherButton").disabled = false;
  }
});


$("loadInsightsButton").addEventListener("click", async () => {
  clearError($("insightsMessage"));

  const state = insightsState.value;
  const district = insightsDistrict.value;

  if (!state || !district) {
    showError($("insightsMessage"), "Select both state and district.");
    return;
  }

  $("insightsLoadState").textContent = "LOADING";
  $("loadInsightsButton").disabled = true;

  try {
    const response = await fetch(
      `/insights/${encodeURIComponent(state)}/${encodeURIComponent(district)}`
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Unable to load field insights.");
    }

    renderInsights(data);

    $("insightsEmpty").classList.add("hidden");
    $("insightsContent").classList.remove("hidden");
    $("insightsLoadState").textContent = "LOADED";
  } catch (error) {
    showError($("insightsMessage"), error.message);
    $("insightsLoadState").textContent = "ERROR";
  } finally {
    $("loadInsightsButton").disabled = false;
  }
});

function renderInsights(data) {
  const summary = data.summary || {};
  const best = summary.best_year || {};
  const worst = summary.worst_year || {};
  const latest = summary.latest_record || {};
  const comparison = data.state_comparison || {};
  const location = data.location || {};
  const period = data.historical_period || {};

  $("insightAverage").textContent =
    summary.average_yield != null
      ? Number(summary.average_yield).toFixed(3)
      : "—";

  $("insightBestYear").textContent =
    best.year ?? "—";

  $("insightBestYield").textContent =
    best.yield != null
      ? `${Number(best.yield).toFixed(3)} t/ha`
      : "—";

  $("insightWorstYear").textContent =
    worst.year ?? "—";

  $("insightWorstYield").textContent =
    worst.yield != null
      ? `${Number(worst.yield).toFixed(3)} t/ha`
      : "—";

  $("insightLatestYear").textContent =
    latest.year ?? "—";

  $("insightLatestYield").textContent =
    latest.yield != null
      ? `${Number(latest.yield).toFixed(3)} t/ha`
      : "—";

  $("insightLocationTitle").textContent =
    `${location.district || "—"}, ${location.state || "—"}`;

  $("comparisonYear").textContent =
    comparison.year ?? "—";

  $("districtComparisonYield").textContent =
    comparison.district_yield != null
      ? `${Number(comparison.district_yield).toFixed(3)} t/ha`
      : "—";

  $("stateComparisonYield").textContent =
    comparison.state_yield != null
      ? `${Number(comparison.state_yield).toFixed(3)} t/ha`
      : "—";

  $("comparisonDifference").textContent =
    comparison.difference_percent != null
      ? `${Number(comparison.difference_percent).toFixed(2)}%`
      : "—";

  if (comparison.difference_percent != null) {
    const diff = Number(comparison.difference_percent);

    if (diff > 0) {
      $("comparisonText").textContent =
        `${location.district} was ${Math.abs(diff).toFixed(2)}% above the ${location.state} state yield in ${comparison.year}.`;
    } else if (diff < 0) {
      $("comparisonText").textContent =
        `${location.district} was ${Math.abs(diff).toFixed(2)}% below the ${location.state} state yield in ${comparison.year}.`;
    } else {
      $("comparisonText").textContent =
        `${location.district} matched the state yield in ${comparison.year}.`;
    }
  } else {
    $("comparisonText").textContent =
      "State comparison is unavailable for the latest district year.";
  }

  $("latestRecordYear").textContent =
    latest.year ?? "—";

  $("latestRecordYield").textContent =
    latest.yield != null
      ? `${Number(latest.yield).toFixed(3)} t/ha`
      : "—";

  $("latestRecordArea").textContent =
    latest.area_hectares != null
      ? `${Number(latest.area_hectares).toLocaleString()} ha`
      : "—";

  $("latestRecordProduction").textContent =
    latest.production_tonnes != null
      ? `${Number(latest.production_tonnes).toLocaleString()} t`
      : "—";

  $("historyPeriod").textContent =
    period.start_year != null && period.end_year != null
      ? `${period.start_year}–${period.end_year}`
      : "—";

  const historyBody = $("historyBody");
  historyBody.innerHTML = "";

  for (const record of data.district_trend || []) {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${record.year ?? "—"}</td>
      <td>${record.area_hectares != null ? Number(record.area_hectares).toLocaleString() : "—"}</td>
      <td>${record.production_tonnes != null ? Number(record.production_tonnes).toLocaleString() : "—"}</td>
      <td>${record.yield_tonnes_per_hectare != null ? Number(record.yield_tonnes_per_hectare).toFixed(3) : "—"}</td>
    `;

    historyBody.appendChild(row);
  }

  drawYieldChart(
    data.district_trend || [],
    data.state_trend || []
  );
}

function drawYieldChart(districtTrend, stateTrend) {
  const svg = $("yieldTrendChart");
  svg.innerHTML = "";

  if (!districtTrend.length) {
    svg.innerHTML = `
      <text x="500" y="180" text-anchor="middle" font-size="18" fill="#68736d">
        No trend data available
      </text>
    `;
    return;
  }

  const stateMap = new Map(
    stateTrend.map(item => [
      Number(item.year),
      Number(item.yield_tonnes_per_hectare)
    ])
  );

  const points = districtTrend.map(item => ({
    year: Number(item.year),
    district: Number(item.yield_tonnes_per_hectare),
    state: stateMap.has(Number(item.year))
      ? stateMap.get(Number(item.year))
      : null
  }));

  const allValues = [];

  for (const point of points) {
    if (Number.isFinite(point.district)) allValues.push(point.district);
    if (Number.isFinite(point.state)) allValues.push(point.state);
  }

  if (!allValues.length) return;

  let minY = Math.min(...allValues);
  let maxY = Math.max(...allValues);

  const padding = Math.max((maxY - minY) * 0.15, 0.2);
  minY = Math.max(0, minY - padding);
  maxY = maxY + padding;

  const width = 1000;
  const height = 360;
  const left = 68;
  const right = 28;
  const top = 24;
  const bottom = 52;

  const plotWidth = width - left - right;
  const plotHeight = height - top - bottom;

  const x = index => {
    if (points.length === 1) return left + plotWidth / 2;
    return left + (index / (points.length - 1)) * plotWidth;
  };

  const y = value => {
    return top + ((maxY - value) / (maxY - minY)) * plotHeight;
  };

  const ns = "http://www.w3.org/2000/svg";

  function line(x1, y1, x2, y2, stroke, widthValue = 1, dash = null) {
    const el = document.createElementNS(ns, "line");
    el.setAttribute("x1", x1);
    el.setAttribute("y1", y1);
    el.setAttribute("x2", x2);
    el.setAttribute("y2", y2);
    el.setAttribute("stroke", stroke);
    el.setAttribute("stroke-width", widthValue);
    if (dash) el.setAttribute("stroke-dasharray", dash);
    svg.appendChild(el);
  }

  function textNode(xValue, yValue, text, anchor = "middle") {
    const el = document.createElementNS(ns, "text");
    el.setAttribute("x", xValue);
    el.setAttribute("y", yValue);
    el.setAttribute("text-anchor", anchor);
    el.setAttribute("font-size", "12");
    el.setAttribute("fill", "#68736d");
    el.textContent = text;
    svg.appendChild(el);
  }

  for (let i = 0; i <= 4; i++) {
    const value = maxY - ((maxY - minY) / 4) * i;
    const yy = top + (plotHeight / 4) * i;

    line(left, yy, width - right, yy, "#dde3df");
    textNode(left - 12, yy + 4, value.toFixed(2), "end");
  }

  line(left, top, left, height - bottom, "#9ca7a0");
  line(left, height - bottom, width - right, height - bottom, "#9ca7a0");

  const labelStep = Math.max(1, Math.ceil(points.length / 8));

  points.forEach((point, index) => {
    if (index % labelStep === 0 || index === points.length - 1) {
      textNode(x(index), height - bottom + 25, point.year);
    }
  });

  function createPolyline(values, stroke, strokeWidth) {
    const usable = values
      .map((value, index) => {
        if (value == null || !Number.isFinite(value)) return null;
        return `${x(index)},${y(value)}`;
      })
      .filter(Boolean);

    if (usable.length < 2) return;

    const poly = document.createElementNS(ns, "polyline");
    poly.setAttribute("points", usable.join(" "));
    poly.setAttribute("fill", "none");
    poly.setAttribute("stroke", stroke);
    poly.setAttribute("stroke-width", strokeWidth);
    poly.setAttribute("stroke-linejoin", "round");
    poly.setAttribute("stroke-linecap", "round");
    svg.appendChild(poly);
  }

  createPolyline(
    points.map(p => p.state),
    "#7d8781",
    2
  );

  createPolyline(
    points.map(p => p.district),
    "#2e6b49",
    3
  );

  points.forEach((point, index) => {
    if (!Number.isFinite(point.district)) return;

    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", x(index));
    circle.setAttribute("cy", y(point.district));
    circle.setAttribute("r", 4);
    circle.setAttribute("fill", "#2e6b49");
    svg.appendChild(circle);
  });
}

document.querySelectorAll(".nav-item[data-view]").forEach(button => {
  button.addEventListener("click", async () => {
    document
      .querySelectorAll(".nav-item[data-view]")
      .forEach(item => item.classList.remove("active"));

    button.classList.add("active");

    document
      .querySelectorAll(".view")
      .forEach(view => view.classList.remove("active-view"));

    $(button.dataset.view).classList.add("active-view");

    if (button.dataset.view === "weatherView") {
      $("pageCrumb").textContent =
        "OPERATIONS / WEATHER ADVISORY";

      $("pageTitle").textContent =
        "Weather & Irrigation Console";

      if (stateSelect.value && !weatherState.value) {
        weatherState.value = stateSelect.value;

        try {
          await fillDistricts(
            weatherDistrict,
            weatherState.value
          );

          if (districtSelect.value) {
            weatherDistrict.value =
              districtSelect.value;
          }
        } catch {}
      }
    }

    if (button.dataset.view === "insightsView") {
      $("pageCrumb").textContent =
        "OPERATIONS / FIELD INSIGHTS";

      $("pageTitle").textContent =
        "Historical Field Insights";

      if (stateSelect.value && !insightsState.value) {
        insightsState.value = stateSelect.value;

        try {
          await fillDistricts(
            insightsDistrict,
            insightsState.value
          );

          if (districtSelect.value) {
            insightsDistrict.value =
              districtSelect.value;
          }
        } catch {}
      }
    }

    if (button.dataset.view === "yieldView") {
      $("pageCrumb").textContent =
        "OPERATIONS / YIELD PREDICTION";

      $("pageTitle").textContent =
        "Yield Operations Console";
    }
  });
});

populateYears();
checkHealth();
initializeLocations();
