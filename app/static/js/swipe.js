(function () {
  const card = document.getElementById("movie-card");
  if (!card) return;

  const movieId = card.dataset.movieId;
  const likeHint = card.querySelector(".swipe-hint.like");
  const dislikeHint = card.querySelector(".swipe-hint.dislike");

  let startX = 0,
    currentX = 0,
    isDragging = false;
  const THRESHOLD = 100;

  card.addEventListener(
    "touchstart",
    (e) => {
      startX = e.touches[0].clientX;
      isDragging = true;
      card.classList.add("dragging");
    },
    { passive: true },
  );

  card.addEventListener(
    "touchmove",
    (e) => {
      if (!isDragging) return;
      currentX = e.touches[0].clientX - startX;
      applyDrag(currentX);
    },
    { passive: true },
  );

  card.addEventListener("touchend", () => finishDrag());

  card.addEventListener("mousedown", (e) => {
    startX = e.clientX;
    isDragging = true;
    card.classList.add("dragging");
    e.preventDefault();
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    currentX = e.clientX - startX;
    applyDrag(currentX);
  });

  window.addEventListener("mouseup", () => {
    if (isDragging) finishDrag();
  });

  function applyDrag(dx) {
    const rotate = dx / 20;
    card.style.transform = `translateX(${dx}px) rotate(${rotate}deg)`;
    const ratio = Math.min(Math.abs(dx) / THRESHOLD, 1);
    if (dx > 0) {
      likeHint.style.opacity = ratio;
      dislikeHint.style.opacity = 0;
    } else {
      dislikeHint.style.opacity = ratio;
      likeHint.style.opacity = 0;
    }
  }

  function finishDrag() {
    isDragging = false;
    card.classList.remove("dragging");
    likeHint.style.opacity = 0;
    dislikeHint.style.opacity = 0;

    if (currentX > THRESHOLD) {
      sendSwipe("like");
    } else if (currentX < -THRESHOLD) {
      sendSwipe("dislike");
    } else {
      card.style.transform = "";
    }
    currentX = 0;
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") sendSwipe("like");
    if (e.key === "ArrowLeft") sendSwipe("dislike");
  });

  document
    .getElementById("btn-like")
    ?.addEventListener("click", () => sendSwipe("like"));
  document
    .getElementById("btn-dislike")
    ?.addEventListener("click", () => sendSwipe("dislike"));

  function sendSwipe(direction) {
    card.classList.add(direction === "like" ? "swipe-right" : "swipe-left");

    const form = new FormData();
    form.append("movie_id", movieId);
    form.append("direction", direction);

    fetch("/swipe", { method: "POST", body: form })
      .then(() => {
        setTimeout(() => location.reload(), 380);
      })
      .catch(() => location.reload());
  }
})();
