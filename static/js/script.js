window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

/*
* @Resource : https://css-tricks.com/snippets/jquery/make-jquery-contains-case-insensitive/
* @Info : This snippet allow us to make the contains function of jquery transform the text to uppercase 
*/
$.expr[":"].contains = $.expr.createPseudo(function(arg) {
  return function( elem ) {
      return $(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
  };
});

/*
* End of the function
*/

$(document).ready(()=>{
  $("#filter-shows").on("keyup",(val)=>{
    string = val.target.value.toUpperCase()
    shows = $(`.show-card:not(:contains('${string}'))`).hide()
    shows = $(`.show-card:contains('${string}')`).show()
  }
  )
})