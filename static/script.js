document.addEventListener('DOMContentLoaded', function() {
  // Auto-fill today's date on log page
  var dateInput = document.getElementById('dateInput');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0,10);
  }

  // Filter workouts by muscle group
  var filter = document.getElementById('muscleFilter');
  if(filter){
    filter.addEventListener('change', function(){
      var val = this.value;
      document.querySelectorAll('#workoutTable tbody tr').forEach(function(row){
        row.style.display = (!val || row.dataset.muscle === val) ? '' : 'none';
      });
    });
  }

  // Toggle new exercise form
  var toggleFormBtn = document.getElementById('toggleForm');
  var exerciseForm = document.getElementById('exerciseForm');
  var cancelAdd = document.getElementById('cancelAdd');
  if(toggleFormBtn && exerciseForm){
    toggleFormBtn.addEventListener('click', function(){
      exerciseForm.style.display = (exerciseForm.style.display === 'block') ? 'none' : 'block';
    });
  }
  if(cancelAdd && exerciseForm){
    cancelAdd.addEventListener('click', function(){
      exerciseForm.style.display = 'none';
    });
  }

  // Add new log entry
  var addEntryBtn = document.getElementById('addEntry');
  var entriesDiv = document.getElementById('entries');
  if(addEntryBtn && entriesDiv){
    addEntryBtn.addEventListener('click', function(){
      var first = entriesDiv.querySelector('.entry');
      if(first){
        var clone = first.cloneNode(true);
        clone.querySelectorAll('input').forEach(function(inp){ inp.value = inp.defaultValue; });
        clone.querySelectorAll('select').forEach(function(sel){ sel.selectedIndex = 0; });
        var rm = document.createElement('button');
        rm.type = 'button';
        rm.textContent = '削除';
        rm.className = 'removeEntry';
        clone.appendChild(rm);
        entriesDiv.appendChild(clone);
      }
    });
  }

  document.addEventListener('click', function(e){
    if(e.target.classList.contains('removeEntry')){
      e.target.parentElement.remove();
    }
  });

  // allow manual weight input
  var logForm = document.getElementById('logForm');
  if(logForm){
    logForm.addEventListener('submit', function(){
      document.querySelectorAll('input[name="weight"]').forEach(function(inp){
        inp.removeAttribute('step');
      });
    });
  }

  // modal handling
  var modal = document.getElementById('modal');
  var modalBody = document.getElementById('modalBody');
  if(modal){
    modal.querySelector('.close').addEventListener('click', function(){
      modal.style.display = 'none';
    });
    modal.addEventListener('click', function(e){
      if(e.target === modal){
        modal.style.display = 'none';
      }
    });
  }

  // calendar popup
  document.querySelectorAll('.calendar td[data-date]').forEach(function(td){
    td.addEventListener('click', function(){
      var date = this.dataset.date;
      fetch('/day_data/' + date)
        .then(r => r.json())
        .then(function(data){
          if(!data.length){
            modalBody.innerHTML = '<p>記録がありません。</p>';
          }else{
            var html = '<table><tr><th>種目</th><th>部位</th><th>セット</th><th>回数</th><th>重量</th></tr>';
            data.forEach(function(row){
              html += '<tr><td>'+row.name+'</td><td>'+row.muscle_group+'</td><td>'+row.sets+'</td><td>'+row.reps+'</td><td>'+row.weight+'</td></tr>';
            });
            html += '</table>';
            modalBody.innerHTML = '<h3>'+date+'</h3>' + html;
          }
          modal.style.display = 'flex';
        });
    });
  });

  // edit workout popup
  document.querySelectorAll('.edit-workout').forEach(function(el){
    el.addEventListener('click', function(e){
      e.preventDefault();
      var id = this.dataset.id;
      fetch('/edit_workout_form/' + id)
        .then(r => r.text())
        .then(function(html){
          modalBody.innerHTML = html;
          modal.style.display = 'flex';
          var form = document.getElementById('editWorkoutForm');
          form.addEventListener('submit', function(ev){
            ev.preventDefault();
            fetch('/edit_workout/' + id, {method:'POST', body:new FormData(form)})
              .then(function(){ location.reload(); });
          });
        });
    });
  });

  // exercise note popup
  document.querySelectorAll('.exercise-note').forEach(function(el){
    el.addEventListener('click', function(e){
      var note = this.dataset.note;
      if(note){
        modalBody.innerHTML = '<p>'+note+'</p>';
        modal.style.display = 'flex';
      }
      e.preventDefault();
    });
  });
});
