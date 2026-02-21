/* ================= SCROLL REVEAL ================= */

const reveals = document.querySelectorAll('.reveal');

function revealOnScroll() {
    reveals.forEach(el => {
        const top = el.getBoundingClientRect().top;
        if (top < window.innerHeight - 100) {
            el.classList.add('show');
        }
    });
}

window.addEventListener('scroll', revealOnScroll);
window.addEventListener('load', revealOnScroll);


/* ================= COUNTERS ================= */

const counters = document.querySelectorAll('.count');
let counterStarted = false;

function startCounters() {

    counters.forEach(counter => {

        const target = +counter.dataset.target;
        let count = 0;
        const speed = 2000; // total animation time
        const increment = target / (speed / 16);

        function update() {
            count += increment;

            if (count < target) {
                counter.innerText = Math.ceil(count);
                requestAnimationFrame(update);
            } else {
                counter.innerText = target;
            }
        }

        update();
    });
}

function checkCounterScroll() {
    const section = document.querySelector('.counters');
    if (!section) return;

    const sectionTop = section.getBoundingClientRect().top;

    if (sectionTop < window.innerHeight - 100 && !counterStarted) {
        counterStarted = true;
        startCounters();
    }
}

window.addEventListener('scroll', checkCounterScroll);
window.addEventListener('load', checkCounterScroll);


/* ================= TESTIMONIAL SLIDER ================= */

const slides = document.querySelectorAll('.slide');
let index = 0;

if (slides.length > 0) {
    setInterval(() => {
        slides[index].classList.remove('active');
        index = (index + 1) % slides.length;
        slides[index].classList.add('active');
    }, 3000);
}
