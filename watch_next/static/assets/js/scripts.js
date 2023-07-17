const btn = document.querySelector('.btn');

btn.addEventListener('click', () => {
    btn.style.backgroundColor = '#555555';
    btn.style.boxShadow = '0 0 40px #555555';
    btn.style.transition = '.5s ease';
});