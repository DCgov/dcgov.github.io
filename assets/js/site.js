$('.clickable').one('click', function() {
	$(this).removeClass('clickable');
	$(this).find('.show').toggle();
	$(this).find('.hide').toggle();
});