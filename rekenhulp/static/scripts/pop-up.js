function annulerenPopUp(check, getal) {
    /**
     * Summary. In deze functie wordt de zichtbaarheid van de pop-up
     * bepaald met de juiste style.
     * @param {boolean} check boolean geeft aan of de pop-up
     * zichtbaar moet zijn
     * @param {number} getal cijfer geeft aan om welke rij het gaat
     * uit de tabel gaat
     */
    var test = document.getElementById("eerste_regel" + getal).innerHTML
    document.getElementById("test").innerHTML = '<a href="/delete/' +
        test +'/"><button type="button" id="verwijderen">Verwijderen</button></a>'
    popUp = document.getElementById('pop-up')
    document.getElementById("tekst_popup").innerText = "Weet u zeker " +
        "dat u Sondevoeding " + test + " wilt verwijderen?"
    if (check === true) {
      popUp.style.display = "block";
    } else {
      popUp.style.display = "none";
    }
}