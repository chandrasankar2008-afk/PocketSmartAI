async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options
  });

  const data = await response
    .json()
    .catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.detail || "Request failed"
    );
  }

  return data;
}


function money(value) {
  return new Intl.NumberFormat(
    "en-IN",
    {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0
    }
  ).format(Number(value || 0));
}


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function linksHtml(links = {}) {
  return Object.entries(links)
    .map(
      ([name, url]) =>
        `<a href="${escapeHtml(url)}"
            target="_blank"
            rel="noopener noreferrer">
            ${escapeHtml(name)}
         </a>`
    )
    .join("");
}


function renderRecommendations(
  data,
  planner
) {
  const root =
    document.getElementById(
      "results"
    );

  if (!root) return;

  const list =
    data.recommendations ||
    data.jewelry_recommendations ||
    [];

  const title =
    planner === "home"
      ? "Home recommendations"
      : planner === "party"
      ? "Party recommendations"
      : "Jewelry recommendations";

  const cards = list
    .map(
      (item) => `
      <article class="rec-card">

        <span class="badge">
          ${escapeHtml(
            item.category ||
            item.item_type ||
            "Recommendation"
          )}
        </span>

        <h4>
          ${escapeHtml(
            item.name ||
            item.description ||
            "Suggested item"
          )}
        </h4>

        <p>
          ${escapeHtml(
            item.description || ""
          )}
        </p>

        <div class="price">
          ${money(
            item.estimated_price
          )}
        </div>

        <small>
          Quantity:
          ${escapeHtml(
            item.quantity || 1
          )}
        </small>

        <div class="links">
          ${linksHtml(
            item.shopping_links || {}
          )}
        </div>

      </article>
      `
    )
    .join("");

  const tips = (
    data.tips ||
    data.styling_tips ||
    []
  )
    .map(
      (tip) =>
        `<li>${escapeHtml(
          tip
        )}</li>`
    )
    .join("");

  const outfitAnalysis =
    data.outfit_analysis
      ? `
        <div class="tips">
          <strong>
            Outfit analysis
          </strong>

          <p>
            ${escapeHtml(
              data.outfit_analysis.style ||
              "Style"
            )}
            ·
            ${escapeHtml(
              data.outfit_analysis.formality ||
              "Occasion-ready"
            )}

            ${
              data.outfit_analysis
                .colors?.length
                ? " · " +
                  escapeHtml(
                    data.outfit_analysis.colors.join(
                      ", "
                    )
                  )
                : ""
            }
          </p>
        </div>
      `
      : "";

  root.innerHTML = `
    <div class="result-shell">

      <div class="result-head">

        <div>

          <span class="badge">
            ${
              data.source === "gemini"
                ? "Gemini AI"
                : "Fallback engine"
            }
          </span>

          <h2>
            ${title}
          </h2>

        </div>

        <span class="badge">
          Saved #${
            data.recommendation_id || ""
          }
        </span>

      </div>


      <div class="budget-row">

        <div class="stat">
          <small>
            Total budget
          </small>

          <strong>
            ${money(
              data.total_budget
            )}
          </strong>
        </div>


        <div class="stat">
          <small>
            Remaining
          </small>

          <strong>
            ${money(
              data.remaining_budget
            )}
          </strong>
        </div>


        <div class="stat">
          <small>
            Items
          </small>

          <strong>
            ${list.length}
          </strong>
        </div>

      </div>


      ${outfitAnalysis}


      <div class="rec-grid">
        ${
          cards ||
          "<p>No recommendations were returned.</p>"
        }
      </div>


      <div class="tips">

        <strong>
          Tips
        </strong>

        <ul>
          ${tips}
        </ul>

      </div>

    </div>
  `;

  root.scrollIntoView({
    behavior: "smooth",
    block: "start"
  });
}


function showError(
  message
) {
  const element =
    document.getElementById(
      "planner-message"
    ) ||
    document.getElementById(
      "form-message"
    );

  if (element) {
    element.textContent = message;
  }
}


async function setupAuth() {
  const isLogin =
    window.PS_AUTH_PAGE ===
    "login";

  const form =
    document.getElementById(
      isLogin
        ? "login-form"
        : "register-form"
    );

  if (!form) return;

  form.addEventListener(
    "submit",
    async (event) => {
      event.preventDefault();

      const message =
        document.getElementById(
          "form-message"
        );

      message.textContent =
        "Please wait…";

      const payload = isLogin
        ? {
            email:
              form.email.value,
            password:
              form.password.value
          }
        : {
            name:
              form.name.value,
            email:
              form.email.value,
            password:
              form.password.value
          };

      try {
        await api(
          isLogin
            ? "/login"
            : "/register",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json"
            },
            body:
              JSON.stringify(
                payload
              )
          }
        );

        window.location.href =
          "/dashboard";

      } catch (error) {
        message.textContent =
          error.message;
      }
    }
  );
}


function formToJson(form) {
  const formData =
    new FormData(form);

  const data = {};

  for (
    const [key, value]
    of formData.entries()
  ) {

    if (
      key === "rooms"
    ) {

      (
        data.rooms ||= []
      ).push(value);

    } else if (
      key === "catering" ||
      key === "decoration" ||
      key === "entertainment" ||
      key === "accommodation"
    ) {

      data[key] = true;

    } else if (
      value !== ""
    ) {

      data[key] = value;
    }
  }

  return data;
}


async function setupPlanner() {
  const planner =
    window.PS_PLANNER;

  if (!planner) return;

  const form =
    document.getElementById(
      `${planner}-form`
    );

  if (!form) return;

  form.addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const button =
        form.querySelector(
          'button[type="submit"]'
        );

      button.disabled = true;

      showError(
        "Generating your plan…"
      );

      try {

        let data;

        if (
          planner === "jewelry"
        ) {

          const formData =
            new FormData(form);

          data = await api(
            "/generate-jewelry",
            {
              method: "POST",
              body: formData
            }
          );

        } else {

          const payload =
            formToJson(form);

          if (
            planner === "home" &&
            (
              !payload.rooms ||
              payload.rooms.length === 0
            )
          ) {

            throw new Error(
              "Select at least one room."
            );
          }

          [
            "total_budget",
            "lights",
            "ceiling_fans",
            "dining_tables",
            "furniture",
            "guests"
          ].forEach(
            (key) => {

              if (
                payload[key] !==
                undefined
              ) {

                payload[key] =
                  Number(
                    payload[key]
                  );
              }
            }
          );

          [
            "catering",
            "decoration",
            "entertainment",
            "accommodation"
          ].forEach(
            (key) => {

              if (
                payload[key] ===
                undefined
              ) {

                payload[key] =
                  false;
              }
            }
          );

          data = await api(
            planner === "home"
              ? "/generate-home"
              : "/generate-party",
            {
              method: "POST",
              headers: {
                "Content-Type":
                  "application/json"
              },
              body:
                JSON.stringify(
                  payload
                )
            }
          );
        }

        showError("");

        renderRecommendations(
          data,
          planner
        );

      } catch (error) {

        showError(
          error.message
        );

      } finally {

        button.disabled =
          false;
      }
    }
  );
}


async function loadHistory(
  targetId,
  limit = 20
) {
  const root =
    document.getElementById(
      targetId
    );

  if (!root) return;

  try {

    const data =
      await api(
        "/api/history"
      );

    const items =
      data.items.slice(
        0,
        limit
      );

    root.innerHTML =
      items.length
        ? items
            .map(
              (item) => `
              <div
                class="history-card"
              >

                <div>

                  <span class="badge">
                    ${escapeHtml(
                      item.planner
                    )}
                  </span>

                  <h3>
                    Recommendation #${
                      item.id
                    }
                  </h3>

                  <p>
                    ${new Date(
                      item.created_at
                    ).toLocaleString()}
                    · Budget
                    ${money(
                      item.request
                        .total_budget
                    )}
                  </p>

                </div>

                <a
                  class="button secondary"
                  href="/history#item-${item.id}"
                >
                  View
                </a>

              </div>
              `
            )
            .join("")
        : `
          <div class="loading">
            No recommendations
            saved yet.
          </div>
        `;

  } catch (error) {

    root.innerHTML = `
      <div class="form-message">
        ${escapeHtml(
          error.message
        )}
      </div>
    `;
  }
}


setupAuth();

setupPlanner();

loadHistory(
  "recent-list",
  5
);

loadHistory(
  "history-list",
  50
)