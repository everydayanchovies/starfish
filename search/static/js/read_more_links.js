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
        if (card.classList.contains("expanded")) {
          var wikiHref = linkEl.dataset.wikiHref;
          if (wikiHref) {
            window.location = wikiHref;
          } else {
            card.classList.remove("expanded");
            linkEl.textContent = "Read more...";
          }
        } else {
          card.classList.add("expanded");
          linkEl.textContent = "Wikipedia...";
        }
      } else {
        window.location = linkEl.dataset.wikiHref;
      }
    }
  }
}
