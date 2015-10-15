
(function($)
{
    //    $(document).ready(function () {
    $(window).bind("load", function(){
        //refreshtime=20000;

        window_height=$(window).height();
        window_width=$(window).width()
        console.log("window_height",window_height);
        console.log("window_width",window_width);
            // so far doesnt do much
            // it reads the height and width of the browser that is used

        $('#Cancel').click
            // this function allows cancelling a standing offer
            // The function is bound to the button with id="#Cancel" in the template
            // Clicking the button activates this function.
            // Then by "loading a page", through the urls.py, views.cancel_so is called
            // the variables are there to identify the player (he is identified by group_id and id_in_group
        (function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();
                var $my_standing_offer = $('#my_standing_offer');
                $my_standing_offer.load('/' + group_id + '/' + id_in_group +'/dAuction2/cancel_so/');
            }
        );


        $('#theoretical_predictions_button').click
            // this function toggles showing or hiding the theoretical predictions (this is a graph
            // with demand-supply analysis
            // The function is bound to the button with id="#theoretical_predictions_button" in the template
            // Clicking the button activates this function.
            // Then by "loading a page", through the urls.py,  views.show_theory is called
            // the variables are there to identify the player (he is identified by group_id and id_in_group
        (function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();

                $.get('/' + group_id + '/' + id_in_group +'/dAuction2/show_theory/', function (data) {});
            }
        );

        $('#stop_button').click
             // this function toggles the auction on or off
            // The function is bound to the button with id="#stop_button" in the template
            // Clicking the button activates this function.
            // Then by "loading a page", through the urls.py,  views.stop is called
            // the variables are there to identify the player (he is identified by group_id and id_in_group
        (function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();

                $.get('/' + group_id + '/' + id_in_group +'/dAuction2/stop/', function (data) {});
            }
        );

        $('#btnSell').click
             // this function results in a new offer for selling, with the price as in the field "#priceInput"
             // and the number of units as in the field "#unitsInput"
            // The function is bound to the button with id="#btnSell" in the template
            // Clicking the button activates this function.
            // Then by "loading a page", through the urls.py,  views.set_offer is called
            // the variables are there to identify the player (he is identified by group_id and id_in_group
        (function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();
                var valUnits = $('#unitsInput').val();
                var valPrice = $('#priceInput').val();
                var valType = 'SELL';
                //var $c24 = $('#c24');
                //var $container2 = $('#c14');
                var $my_standing_offer = $('#my_standing_offer');
                $my_standing_offer.load('/' + group_id + '/' + id_in_group + '/dAuction2/set_offer/' + valUnits + '/' + valPrice + '/' + valType);
            }
        );


        $('#btnBuy').click
              // this function results in a new offer for buying, with the price as in the field "#priceInput"
             // and the number of units as in the field "#unitsInput"
            // The function is bound to the button with id="#btnSell" in the template
            // Clicking the button activates this function.
            // Then by "loading a page", through the urls.py,  views.set_offer is called
            // the variables are there to identify the player (he is identified by group_id and id_in_group
        (function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();
                var valUnits = $('#unitsInput').val();
                var valPrice = $('#priceInput').val();
                var valType = 'BUY';
                var $container3 = $('#my_standing_offer');
                $container3.load('/' + group_id + '/' + id_in_group + '/dAuction2/set_offer/' + valUnits + '/' + valPrice + '/' + valType);
                //$container.load('dAuction2/all_transactions/'+valUnits+'/'+valPrice);
            }
        );



//        var auto_refresh2 = setInterval
            // this function makes autonomous agents bid. This function is turned off for this version
            // as all players are human subjects

//        (
//            function () {
//                $.get('dAuction2/refresh2/', function (data) {});
//                $.get('dAuction2/refresh2/', function (data) {});

//            }
//            , 2000
//        );
        var auto_refresh = setInterval
            // this function refreshes the information for each player. It results in the procedure
            // index_calculations being run.
            // Then by "loading a page", through the urls.py,  views.refresh is called
            // There index_calculations is ran, calculating from the info in the database the present state of the
            // game.
            // This new information is used to render a page "content_refresh.html" and then the JQUERY takes
            // the information from this page and inserts it into the present page
            // I UNDERSTAND THAT NOT USING JSON MAKES THIS PAGE RENDERING A BIT ARTIFICIAL.
            // BUT USING JSON, I AM NOT ABLE TO SEND AN OBJECT, WHICH "VIOLATES" THE DJANGO LOGIC
            // WHAT IS HERE THE BEST CHOICE?

        (
            function () {
                var group_id = $('#group_idInput').val();
                var id_in_group = $('#id_in_groupInput').val();

                $.get
                ('/'+group_id+'/'+id_in_group+'/'+'dAuction2/refresh/', function (data) {
                        var $all_transactions_digital = $(data).filter('#all_transactions_digital').html();

                        // Now the new info has been calculated through index_calculations
                        // and we have received the new info rendered in the page "content_refresh.html"
                        // The following commands pick the info from this page
                        var $all_transactions = $(data).filter('#all_transactions').html();
                        var $all_transactions_text = $(data).filter('#all_transactions_text').html();
                        var $theoretical_predictions = $(data).filter('#theoretical_predictions').html();
                        var $theoretical_predictions_text = $(data).filter('#theoretical_predictions_text').html();
                        var $all_standing_market_offers = $(data).filter('#all_standing_market_offers').html();
                        var $my_standing_offer = $(data).filter('#my_standing_offer').html();
                        var $my_vouchers = $(data).filter('#my_vouchers').html();
                        //console.log('1111111111111111111111111111111111111111111111111111111111111something');


                        // The following commands now past the new info into the different parts of our present
                        // page
                        $('#all_transactions_digital').html($all_transactions_digital);
                        //$('#my_cleared_offers').html($my_cleared_offers);
                        $('#all_transactions').html($all_transactions);
                        $('#all_transactions_text').html($all_transactions_text);
                        $('#theoretical_predictions_text').html($theoretical_predictions_text);
                        $('#theoretical_predictions').html($theoretical_predictions);
                        $('#all_standing_market_offers').html($all_standing_market_offers);
                        $('#my_standing_offer').html($my_standing_offer);
                        $('#my_vouchers').html($my_vouchers);
                    }
                );
            }
            , 500
        );
    })
}(jQuery));