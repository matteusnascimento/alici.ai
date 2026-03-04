// landing.js
// basic interactions, populate sections with demo content

function createCard(title, text) {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<h3>${title}</h3><p>${text}</p>`;
    return card;
}

window.addEventListener('DOMContentLoaded', () => {
    const tech = document.getElementById('technology');
    ['Conversational AI Engine', 'Image Recognition System', 'Audio Intelligence Processing', 'Persistent Database Memory', 'Scalable SaaS Infrastructure']
    .forEach(t => tech.appendChild(createCard(t, 'Lorem ipsum dolor sit amet.')));

    const invest = document.getElementById('investors');
    ['Proprietary Neural System', 'Growing Dataset', 'Scalable Infrastructure', 'Monetization Ready', 'SaaS Architecture']
    .forEach(t => invest.appendChild(createCard(t, 'Lorem ipsum dolor sit amet.')));

    const arch = document.getElementById('architecture');
    arch.innerHTML = '<div class="arch-diagram">Frontend → API → AI Engine → Database → Cloud</div>';

    const cta = document.getElementById('cta');
    cta.innerHTML = '<h2>Build the Next Generation of Intelligence</h2><a href="/dashboard" class="btn primary">Access Platform</a>';
});