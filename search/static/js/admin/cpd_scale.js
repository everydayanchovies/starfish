window.onload = () => {
  let titleH2 = document.querySelector("#content > h2");
  if (!titleH2) {
    titleH2 = document.createElement("h2");
    insertAfter(titleH2, document.querySelector("#content > h1"));
  }

  const scaleParentListContainer =
    document.getElementsByClassName("field-scale_type")[0];
  const scaleParentList = document.getElementById("id_scale_parent");
  const scaleInput = document.getElementById("id_scale");
  const scaleTypeList = document.getElementById("id_scale_type");

  const makeLabel = () => {
    if (scaleParentList.value) {
      return (
        scaleParentList.selectedOptions[0].label.split(" - ")[0] +
        scaleInput.value
      );
    } else {
      return scaleTypeList.selectedOptions[0].value + "-" + scaleInput.value;
    }
  };

  const toggleScaleParent = () => {
    if (scaleParentList.value) {
      scaleParentListContainer.style.display = "none";
    } else {
      scaleParentListContainer.style.display = "block";
    }
  };

  const updateLabel = () => {
    titleH2.textContent = "Scale label: " + makeLabel();
    toggleScaleParent();
  };

  scaleParentList.onchange = updateLabel;
  scaleInput.onkeyup = updateLabel;
  scaleTypeList.onchange = updateLabel;

  updateLabel();
};

function insertAfter(newNode, referenceNode) {
  referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
