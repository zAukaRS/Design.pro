document.addEventListener("DOMContentLoaded", function() {
    const bubbleContainer = document.querySelector(".bubbles");

    const numBubbles = 15;

    for (let i = 0; i < numBubbles; i++) {
        const bubble = document.createElement("div");
        bubble.classList.add("bubble");

        const size = Math.random() * 30 + 20;
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;

        const positionX = Math.random() * 100;
        const positionY = Math.random() * 100;
        bubble.style.left = `${positionX}%`;
        bubble.style.top = `${positionY}%`;

        const duration = Math.random() * 4 + 3;
        bubble.style.animationDuration = `${duration}s`;

        const delay = Math.random() * 2;
        bubble.style.animationDelay = `${delay}s`;

        bubbleContainer.appendChild(bubble);
    }
});
