const selected_dict = {};


function addItem(element) {
    const date_tuple = element.value;

    if (selected_dict[date_tuple]) {
        element.style.backgroundColor = "lightyellow";
        delete selected_dict[date_tuple];
    } else {
        element.style.backgroundColor = "green";
        selected_dict[date_tuple] = true;
    }

    console.log(date_tuple);
    console.log(selected_dict);
}


const addContent = (ev) => {
    ev.preventDefault();
    let shifts_list = {
        publish_date: Date.now(),
        shifts: selected_dict,
    }
    document.getElementById("result").value = JSON.stringify(shifts_list);
    let confirmation = confirm("Do you confirm to proceed?")
    if (confirmation) {
        const url = window.location.href;
        document.getElementById('shifts_to_send').submit();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('submit_button').addEventListener('click', addContent);
});
