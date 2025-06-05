// ページ読み込み後に各種処理を設定
document.addEventListener('DOMContentLoaded', function() {
  // ログ入力ページの日付を自動で本日にする
  var dateInput = document.getElementById('dateInput');
  if (dateInput && !dateInput.value) {
    dateInput.value = new Date().toISOString().slice(0,10);
  }

  // 部位フィルターによる表示切り替え
  var filter = document.getElementById('muscleFilter');
  if(filter){
    filter.addEventListener('change', function(){
      var val = this.value;
      document.querySelectorAll('#workoutTable tbody tr').forEach(function(row){
        row.style.display = (!val || row.dataset.muscle === val) ? '' : 'none';
      });
    });
  }

  // 新しいエクササイズ入力フォームの表示切替
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

  // 種目入力欄をもう一行追加
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

  // 重量欄の手入力を許可
  var logForm = document.getElementById('logForm');
  if(logForm){
    logForm.addEventListener('submit', function(){
      document.querySelectorAll('input[name="weight"]').forEach(function(inp){
        inp.removeAttribute('step');
      });
    });
  }

  // モーダルの表示・非表示を制御
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

  // カレンダーの日付をクリックしたときのポップアップ
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

  // 編集ボタンを押したときのワークアウト編集モーダル
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

  // 種目名クリックでメモを表示
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

  // エクササイズ編集モーダル
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
});
// ここまでJavaScriptの処理
