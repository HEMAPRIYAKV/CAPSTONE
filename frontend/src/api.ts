const API_BASE_URL = "http://127.0.0.1:8000";

export async function fetchLivePrediction() {
  const response = await fetch(`${API_BASE_URL}/live-predict`, {
    method: "GET",
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json();
}

export async function fetchEvacuationData(
  latitude: number,
  longitude: number,
  networkDistance = 5000
) {
  const response = await fetch(`${API_BASE_URL}/evacuation-auto`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      latitude,
      longitude,
      network_distance: networkDistance,
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json();
}
