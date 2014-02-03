$(function(){
	$("select[name='per_page'], select[name='sort']").selectpicker({style: 'btn-default', menuStyle: 'dropdown-inverse'});
});	

$(document).ready(function(){
	var q = window.location.search,
	params = {
		load_results: 'load=',
		search_term: 'term=',
		per_page: 'per_page=',
		sort: 'sort=',
		adv:  'adv='
	};

	q = q.substring(1,q.length);

	var load = q.substring(q.indexOf(params.load_results)+params.load_results.length, q.indexOf(params.search_term)),
	term = getParam(q,params.search_term),
	per_page = getParam(q,params.per_page),
	sort = getParam(q,params.sort);

	function getParam(q,term){
		var str = q.substring(q.indexOf(term)+term.length, q.length);
		if(str.indexOf('&')>0)
			str = str.substring(0,str.indexOf('&'));
		return str;
	}

	if(load.replace('&','')=='true'){
		//loadResults();
	}

	if(q.indexOf(params.search_term)>0){
		$('#id_keyword').val(unescape(term));
	}

	if(q.indexOf(params.adv)>0){
		$('.adv.group').slideToggle(0);
	}

	var $perPage = $("#id_per_page + .btn-group .dropdown-toggle .filter-option"),
		currentVisiblePageNumber = $perPage.html().trim();

	var $sort = $("#id_sort + .btn-group .dropdown-toggle .filter-option"),
		currentVisibleSort = $sort.html().trim();

	if(currentVisiblePageNumber !==per_page){
		getCurrentDropdownSetting('per_page', per_page);
	}

	if(currentVisibleSort !==sort){
		getCurrentDropdownSetting('sort', sort);
	}

	function getCurrentDropdownSetting(id, value){
		var val = unescape(value)
		$("#id_"+id+" + .btn-group li span").each(function(){
			var num = $(this).html().trim();
			if(num == val){
				$(this).parents('.dropdown-menu').siblings('button').find('.filter-option').html(num);
				$(this).parents('li').addClass('selected').siblings().removeClass('selected');
			}
		});
	}


	var $form = $('form');

	$( "input" )
  	.keyup(function() {
    var value = $( this ).val();
    $(this).attr('value',value);
	});

	$form.on('keyup',function(e){
		e.preventDefault();
		var code = e.keyCode || e.which,
		$input = $(document.activeElement);

		if(code == 13){
			$(this).submit();
		}
	});
	$(".home form").on('submit',function(e){
		e.preventDefault();
		search.get(true);
	});
	$('#submit').on('click', function(e){
		e.preventDefault();
		search.get();
	});

	$('.home #submit').on('click', function(e){
		e.preventDefault();
		search.get(true);
	});

	$advOptionsGroup =  $(".adv.group");

	$('.adv.group .controls .btn').bind('click', function(e){
		e.preventDefault();

		var $this = $(this);
		if($this.hasClass('submit')){
			search.get();
		}
		else if($this.hasClass('reset')){
			reset($advOptionsGroup);
		}
	});

	function reset(elem){
		var $elem = $(elem),
			$inputs = $elem.find('input');
		$inputs.val('');
	}

	$('.toggle.switch').on('click',function(e){
		e.preventDefault();
		toggleGroup(this);
	});


});//end doc.ready


function toggleGroup(elem){
	var $this = $(elem),
		group = $this.attr('data-type');

	$(this).toggleClass('active');
	$(".group[data-type='"+ group +"']").stop(false,true).slideToggle(500);
}

var search = {
	get: getResults,
	load: loadResults
}


function getResults(move){
	var $form = $('form'),
	protocol = window.location.protocol,
	host = window.location.host,
	path = window.location.pathname;
	query = getQueryStringFromForm($form),
	$keywordInput = $('.input-group input#id_keyword'),
	keyword=$keywordInput.attr('value');

	if(path.indexOf('search')<0){
		path='/search/';
	}
	request = protocol+'//'+host+path+'?'+query;

	// if(keyword!='' && keyword!==undefined){
		$('.dropdown-menu, .dropdown-arrow').hide();

		if(move){
			moveElementsForResults(request);
		}
		else{
			loadResults(request, query);
		}
	// }
	// //keyword input is empty
	// else{
	// 	$keywordInput.parent().addClass('has-error');
	// 	$keywordInput.parent().shake();
	// }
}

function loadResults(request_url){
	$.get(request_url,function(data){
		$data = $('<div/>').attr('class','cards');
		//$data.append(data);
		$results = $('.results');
		$results_listing = $('.results .result-listing');

		$results_listing.css({'opacity':'0'}).html($data);
		$('.results')
		.css({'opacity':'0'})
		.removeClass('hidden')
		.animate({'opacity':'1'},500,function(){
			$results_listing.animate({'opacity':'1'},500);
		});
			
		changeLocation(request_url);
		
	});
}

function moveElementsForResults(url){
	var $header = $('#search h1'),
	$recent = $('.recent'),
	$filter = $('.page-options'),
	$footer =$('.footer');

	if($filter.not(":visible").length>0){
		$filter.slideUp(0);
	}
	$('.slideup').slideUp(500);
	$footer.hide();
	$('.home').css({'background-color':'#F7F7F7'});
	if($filter.not(":visible").length>0){
		$filter.slideDown(500)
		$filter.fadeIn(500);
	}
	$recent.fadeOut(500);
	$header.slideUp(500, function(){
		$(this).animate({'opacity':'0'},1000,function(){
			changeLocation(url);
		})
		
	});
}
function changeLocation(url){
	window.location=url;
}


function getQueryStringFromForm(form){
	var $form = $(form);
	if($form.length<0){
		return '';
	}
	var str ='', count=0;
	$form.find('input').each(function(){
		var $this = $(this);
		if($this.parent('.sr-only').length<=0){
			if($this.attr('name')!=undefined){
				if(count>0){
					str+='&amp;';
				}
				var value = $this.attr('value') || '';
				
				str+=$this.attr('name')+'='+escape(value);
			}
			count++;
		}
	});
	$form.find('select').each(function(){
		var $this = $(this);
		if($this.parent('.sr-only').length<=0){
			if(count>0){
				str+='&amp;';
			}
			str+=$this.attr('name')+'='+$this.children('option:selected').html().trim();
			count++;
		}
	});
	if($('.adv.group:visible').length>0){
		str+='&amp;adv=true';
	}
	return str;
}


function replaceQueryString(url,param,value) {
	var re = new RegExp("([?|&])" + param + "=.*?(&|$)","i");
	if (url.match(re))
		return url.replace(re,'$1' + param + "=" + value + '$2');
	else
		return url + '&' + param + "=" + value;
}

//Shake function
(function( $ ){
   $.fn.shake = function() {
      var $this = $(this);

      $this.animate({'left':'-20px'},40, function(){
      	$(this).animate({left:'10px'},80, function(){
      		$(this).animate({'left':'0px'},50)
      	})
      });

      return this;
   }; 
})( jQuery );


//debug 
function log(){
	console.log.apply(console, arguments);
}

