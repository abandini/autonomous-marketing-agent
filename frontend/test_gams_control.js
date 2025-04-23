/**
 * Simple test script for GAMS control functionality
 */

// Function to test the API endpoint directly
function testGamsControl(action) {
    console.log(`Testing GAMS control with action: ${action}`);
    
    fetch('/api/operator/system/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Response data:', data);
        alert(`GAMS ${action} request successful: ${JSON.stringify(data)}`);
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    });
}

// Add event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, setting up test buttons');
    
    // Add event listeners to test buttons
    document.getElementById('test-start-btn').addEventListener('click', function() {
        console.log('Test start button clicked');
        testGamsControl('start');
    });
    
    document.getElementById('test-stop-btn').addEventListener('click', function() {
        console.log('Test stop button clicked');
        testGamsControl('stop');
    });
});
