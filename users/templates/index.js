  document.getElementById('logo').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('active');
  });
  
  document.getElementById('close-btn').addEventListener('click', function() {
    document.getElementById('sidebar').classList.remove('active');
  });
  document.addEventListener('DOMContentLoaded', function() {
    var todaysMembership = document.getElementById('todays-membership');
    var expiringMembership = document.getElementById('expiring-membership');
    todaysMembership.classList.remove('hidden');
    expiringMembership.classList.remove('hidden');
  });

  document.getElementById('summary-button').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    var todaysBooking = document.getElementById('todays-booking');
    var todaysMembership = document.getElementById('todays-membership');
    var AdvanceBooking = document.getElementById('advance-booking');
    var expiringMembership = document.getElementById('expiring-membership');
    var scroll = document.getElementById('scroll');
    
    if(todaysBooking.classList.contains('tb-height')){
        todaysBooking.classList.remove('tb-height');
        scroll.classList.remove('sh');
        todaysMembership.classList.remove('hidden');
        expiringMembership.classList.remove('hidden');
        AdvanceBooking.classList.remove('hidden');
        sidebar.classList.remove('active');
    }else{
        todaysBooking.classList.add('tb-height');
        scroll.classList.add('sh');
        todaysMembership.classList.add('hidden');
        expiringMembership.classList.add('hidden');
        AdvanceBooking.classList.add('hidden');
        sidebar.classList.remove('active');
    }
    
    
  });
  




// Function to handle barcode scanning
function handleBarcodeScan(event) {
    const barcodeInput = event.target;
    let barcodeValue = barcodeInput.value.trim();

    // Check if barcode length is greater than 10 digits
    if (barcodeValue.length > 10) {
        // Trim to the first 10 digits
        barcodeValue = barcodeValue.slice(0, 10);
    }

    // Check if barcode length is exactly 10 digits
    if (barcodeValue.length === 10) {
        // Reflect scanned barcode value into visible input field
        const visibleBarcodeInput = document.getElementById('barcode');
        if (visibleBarcodeInput) {
            visibleBarcodeInput.value = barcodeValue;
        }

        // Open membership booking popup
        openMembershipBookingPopup(barcodeValue);

        // Clear the barcode input
        barcodeInput.value = '';
    }
}

// Function to open membership booking popup
function openMembershipBookingPopup(barcodeValue) {
    console.log('Opening membership booking popup for barcode:', barcodeValue);
    const popupId = 'membership-booking-popup';
    const popup = document.getElementById(popupId);
    
    // Ensure the popup exists
    if (popup) {
        // Check if popup is already open
        if (!popup.classList.contains('hidden')) {
            console.log('Popup is already open. Scanned barcode:', barcodeValue);
            return; // Exit function if popup is already open
        }
        
        // Perform actions to show the popup
        showPopup(popupId);
        
        // Use barcodeValue to process further actions if needed
        console.log('Opening popup for barcode:', barcodeValue);

        // Optionally, you can add further logic or actions here
    }
}

// Function to show popup
function showPopup(popupId) {
    const popup = document.getElementById(popupId);
    if (popup) {
        popup.classList.remove('hidden');
        
        // Add event listener to close popup when clicking outside the content
        popup.addEventListener('click', function(event) {
            if (event.target === popup) {
                hidePopup(popupId);
            }
        });
    }
}

// Function to hide popup
function hidePopup(popupId) {
    const popup = document.getElementById(popupId);
    if (popup) {
        popup.classList.add('hidden');
        
        // Remove event listener to prevent memory leaks
        popup.removeEventListener('click', function(event) {
            if (event.target === popup) {
                hidePopup(popupId);
            }
        });

        // Return focus to the hidden barcode scanner input
        const barcodeScanner = document.getElementById('barcode-scanner');
        if (barcodeScanner) {
            barcodeScanner.focus();
        }
    }
}

// Ensure focus on hidden barcode scanner input by default
document.addEventListener('DOMContentLoaded', function() {
    const barcodeScanner = document.getElementById('barcode-scanner');
    if (barcodeScanner) {
        barcodeScanner.addEventListener('input', handleBarcodeScan);
        barcodeScanner.focus(); // Ensure focus on load
    }
});

function redirectToManager() {
    window.location.href = 'demo.html';
  }