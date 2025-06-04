document.addEventListener('DOMContentLoaded', function() {
  // Auto-fill today's date on log page
  var dateInput = document.getElementById('dateInput');
  if (dateInput && !dateInput.value) {
    var today = new Date().toISOString().slice(0, 10);
    dateInput.value = today;
  }

  // Filter workouts by muscle group
  var filter = document.getElementById('muscleFilter');
  if (filter) {
    filter.addEventListener('change', function() {
      var value = this.value;
      document.querySelectorAll('#workoutTable tbody tr').forEach(function(row) {
        if (!value || row.dataset.muscle === value) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }

  // Toggle new exercise form
  var toggleFormBtn = document.getElementById('toggleForm');
  var exerciseForm = document.getElementById('exerciseForm');
  if (toggleFormBtn && exerciseForm) {
    toggleFormBtn.addEventListener('click', function() {
      if (exerciseForm.style.display === 'none' || exerciseForm.style.display === '') {
        exerciseForm.style.display = 'block';
      } else {
        exerciseForm.style.display = 'none';
      }
    });
  }
});
