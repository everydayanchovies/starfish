window.onload = () => {
  prepareReadMoreButtons();
};

function prepareReadMoreButtons() {
  const linkEls = document.getElementsByClassName("wiki-link");
  for (var i = 0; i < linkEls.length; i++) {
    let linkEl = linkEls[i];
    let card = linkEl.parentElement.parentElement;
    linkEl.onclick = () => {
      if (card.classList.contains("expandable")) {
        var wikiHref = linkEl.dataset.wikiHref;
        if (card.classList.contains("expanded")) {
          if (wikiHref) {
            window.location = wikiHref;
          } else {
            card.classList.remove("expanded");
            linkEl.textContent = "Read more...";
          }
        } else {
          card.classList.add("expanded");
          if (wikiHref) {
            linkEl.textContent = "Visit...";
          } else {
            linkEl.textContent = "";
          }
        }
      } else {
        window.location = linkEl.dataset.wikiHref;
      }
    }
  }
}
