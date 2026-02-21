const items = document.querySelectorAll('.reveal');

window.addEventListener('scroll', ()=>{
    items.forEach(el=>{
        const top = el.getBoundingClientRect().top;
        if(top < window.innerHeight - 100){
            el.classList.add('show');
        }
    });
});
