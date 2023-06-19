function msg(){
    let a = [',','@', '[', ']', '*', '!', '#', '$', '%', '^', '&', '+', '\'', '\"', '\\', '\/', '.', '?','<', '>', ':', ';', '{', '}', '=', '|' , '`', '~'];
    let st = document.getElementById("query").value;
    console.log(st);
    
    let fl = 0;

    for (let i of a) {
    if (st.includes(i)) {
        fl = 1;
        break;
    }
    }
    if (st.length === 0){
        alert("You have Entered an Empty Query, Please enter some value in the query box");
        return false;    
        }

    else if (fl === 1) {
    alert("You have Entered an Invalid Query, please check the query rules in the home page");
    console.log("You have Entered an Invalid Query, please check the query rules in the home page");
    return false;
    } else {
    alert("Your have entered a Valid Query, you can proceed");
    }

}

function msg1(){
    alert("Hello");
}


