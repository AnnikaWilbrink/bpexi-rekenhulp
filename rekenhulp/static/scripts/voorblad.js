
function bmiBerekenen(){
    /**
     * Summary. In deze functie wordt de BMI berekend met de ingevulde
     * lengte en gewicht. Deze waarde wordt dan op het scherm
     * teruggegeven. Als een van de invoervelden van lengte en/of
     * gewicht leeg zijn dan verdwijnt de BMI van het scherm.
     */
    if (document.getElementById("gewicht") && document.getElementById("gewicht").value && document.getElementById("lengte") && document.getElementById("lengte").value) {
    let gewicht = Number(document.getElementById("gewicht").value);
    let lengte = Number(document.getElementById("lengte").value);
    let bmi = Math.round(((gewicht/(lengte*lengte))*10000)* 10) / 10;
    document.getElementById("bmi-waarde").innerHTML = bmi;
    } else {
    document.getElementById("bmi-waarde").innerHTML = "-";
    }
}


function naamCheck(){
   /**
    * Summary. In deze functie wordt de ingevulde naam gecheckt. Als
    * het invoerveld geen geldige tekens bevat, dan komt er een melding
    * op het scherm tevoorschijn en is de submit knop inactief. Bij een
    * geldige invoer is de knop submit wel actief.
    */
    if (document.getElementById("naam").value !== '') {
        let patientnaam = document.getElementById("naam").value
        let knop = document.getElementById("subknop")
        let regex = patientnaam.match(/[A-Za-zÀ-ú '-.]/g)
        if (!regex || patientnaam.length !== regex.length) {
            document.getElementById("message").innerHTML = 'Incorrecte input'
            knop.classList.add('disabled')
        } else {
            document.getElementById("message").innerHTML = ''
            knop.classList.remove('disabled')
        }
    }
}
