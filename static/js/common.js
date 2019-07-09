
 $(document).ready(function() {

	var $menus = $('.skmu_list_item');

	//open modal

    $menus.on('click', function(event){

            $(event.target.parentNode).addClass('skmu_list_item_on');

	});


});

