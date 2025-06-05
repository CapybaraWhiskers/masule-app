document.addEventListener('DOMContentLoaded', function() {
  // Auto-fill today's date on log page
  var dateInput = document.getElementById('dateInput');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0,10);
  }

  // Filter workouts by muscle group
  var muscleFilter = document.getElementById('muscleFilter');
  var exerciseFilter = document.getElementById('exerciseFilter');

  function updateFilters(){
    var mVal = muscleFilter ? muscleFilter.value : '';
    var eVal = exerciseFilter ? exerciseFilter.value : '';
    document.querySelectorAll('#workoutTable tbody .data-row').forEach(function(row){
      var okMuscle = !mVal || row.dataset.muscle === mVal;
      var okEx = !eVal || row.dataset.exercise === eVal;
      row.style.display = (okMuscle && okEx) ? '' : 'none';
    });
  }

  if(muscleFilter){
    muscleFilter.addEventListener('change', updateFilters);
  }
  if(exerciseFilter){
    exerciseFilter.addEventListener('change', updateFilters);
  }

  document.querySelectorAll('.exercise-filter-link').forEach(function(el){
    el.addEventListener('click', function(e){
      e.preventDefault();
      if(exerciseFilter){
        exerciseFilter.value = this.textContent.trim();
        updateFilters();
      }
    });
  });

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

  function attachExerciseListener(entry){
    var select = entry.querySelector('.exercise-select');
    if(select){
      select.addEventListener('change', function(){
        var opt = this.options[this.selectedIndex];
        var sets = opt.dataset.sets;
        var reps = opt.dataset.reps;
        var weight = opt.dataset.weight;
        if(sets){ entry.querySelector('input[name="sets"]').value = sets; }
        if(reps){ entry.querySelector('input[name="reps"]').value = reps; }
        if(weight){ entry.querySelector('input[name="weight"]').value = weight; }
      });
    }
  }

  if(addEntryBtn && entriesDiv){
    addEntryBtn.addEventListener('click', function(){
      var first = entriesDiv.querySelector('.entry');
      if(first){
        var clone = first.cloneNode(true);
        clone.querySelectorAll('input').forEach(function(inp){ inp.value = inp.defaultValue; });
        clone.querySelectorAll('select').forEach(function(sel){
          var def = Array.from(sel.options).findIndex(function(o){ return o.defaultSelected; });
          sel.selectedIndex = def >= 0 ? def : 0;
        });
        var rm = document.createElement('button');
        rm.type = 'button';
        rm.textContent = '削除';
        rm.className = 'removeEntry';
        clone.appendChild(rm);
        entriesDiv.appendChild(clone);
        attachExerciseListener(clone);
      }
    });
  }

  // attach listener for initial entry
  if(entriesDiv){
    entriesDiv.querySelectorAll('.entry').forEach(function(entry){
      attachExerciseListener(entry);
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

  var logModalBtn = document.getElementById('openLogModal');
  if(logModalBtn){
    logModalBtn.addEventListener('click', function(){
      fetch('/log_form')
        .then(r => r.text())
        .then(function(html){
          modalBody.innerHTML = html;
          modal.style.display = 'flex';
          var entry = modalBody.querySelector('.entry');
          if(entry){ attachExerciseListener(entry); }
          var form = document.getElementById('logFormModal');
          if(form){
            var date = form.querySelector('#dateInputModal');
            if(date && !date.value){
              date.value = new Date().toISOString().slice(0,10);
            }
            form.addEventListener('submit', function(ev){
              ev.preventDefault();
              fetch('/log', {method:'POST', body:new FormData(form)})
                .then(function(){ location.reload(); });
            });
          }
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

  // exercise memo popup
  document.querySelectorAll('.exercise-note').forEach(function(el){
    el.addEventListener('click', function(e){
      var memo = this.dataset.memo;
      var video = this.dataset.video;
      var html = '';
      if(memo){
        html += '<p>'+memo.trim()+'</p>';
      }
      if(video){
        var trimmed = video.trim();
        html += '<p><a href="'+trimmed+'" target="_blank" rel="noopener noreferrer">'+trimmed+'</a></p>';
      }
      if(html){
        modalBody.innerHTML = html;
        modal.style.display = 'flex';
      }
      e.preventDefault();
    });
  });

  // edit exercise popup
  document.querySelectorAll('.edit-exercise').forEach(function(el){
    el.addEventListener('click', function(e){
      e.preventDefault();
      var id = this.dataset.id;
      fetch('/edit_exercise_form/' + id)
        .then(r => r.text())
        .then(function(html){
          modalBody.innerHTML = html;
          modal.style.display = 'flex';
          var form = document.getElementById('editExerciseForm');
          form.addEventListener('submit', function(ev){
            ev.preventDefault();
            fetch('/edit_exercise/' + id, {method:'POST', body:new FormData(form)})
              .then(function(){ location.reload(); });
          });
        });
    });
  });

  // shrink long exercise names
  document.querySelectorAll('.exercise-name').forEach(function(td){
    var max = 130;
    if(td.scrollWidth > max){
      td.style.fontSize = '0.9em';
    }
  });
});
