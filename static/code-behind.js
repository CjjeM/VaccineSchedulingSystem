function changeHospInfo(selectObject) {
    var elem = document.getElementById('hospital-name');

    var current_hospital_name = selectObject.value;
    var hospital_data = $('hospital-name').data('hospital');

    console.log(hospital_data)
    
}