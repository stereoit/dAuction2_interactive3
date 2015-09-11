
$(document).ready( function() {


$('#number_of_units2').click(function(){
    playerid = 1;
    $.get('/dAuction2/add_number/', {player_id: playerid}, function(data){
               $('#like1').html(data);
               $('#like2').html(data);
    });
});


$('#setOffer').click(function(){
    playerid = 1;
    var valUnits=$('#unitsInput').val();
    var valPrice=$('#priceInput').val();
    contextDict={valUnits: valUnits, valPrice: valPrice}
    $.get('/dAuction2/set_offer/',contextDict , function(data){
        $('#price').html(valPrice);
        $('#units').html(valUnits);
    });
});




    });