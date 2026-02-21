document.querySelectorAll('.count').forEach(counter=>{
    const target = +counter.dataset.target;

    let c = 0;
    const update = ()=>{
        if(c < target){
            c += target/40;
            counter.innerText = Math.ceil(c);
            requestAnimationFrame(update);
        }
    }
    update();
});
