// クイズ関連のJavaScript

// タイマー機能
class QuizTimer {
    constructor(duration = 20) {
        this.duration = duration;
        this.timerInterval = null;
        this.onTimeout = null;
        
        // セッションストレージからタイマー情報を復元
        const savedTimer = sessionStorage.getItem('quizTimer');
        if (savedTimer) {
            const timerData = JSON.parse(savedTimer);
            const elapsed = Math.floor((Date.now() - timerData.startTime) / 1000);
            this.timeLeft = Math.max(0, duration - elapsed);
            this.startTime = timerData.startTime;
        } else {
            this.timeLeft = duration;
            this.startTime = Date.now();
        }
        
        this.actualTimeSpent = 0;
    }
    
    start() {
        // 初回起動時のみ開始時間を設定
        if (!sessionStorage.getItem('quizTimer')) {
            this.startTime = Date.now();
            sessionStorage.setItem('quizTimer', JSON.stringify({
                startTime: this.startTime,
                duration: this.duration
            }));
        }
        
        // 既存のタイマーをクリア
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        this.timerInterval = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.stop();
                if (this.onTimeout) {
                    this.onTimeout();
                }
            }
        }, 1000);
    }
    
    stop() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.actualTimeSpent = Math.round((Date.now() - this.startTime) / 1000);
        // セッションストレージをクリア
        sessionStorage.removeItem('quizTimer');
    }
    
    updateDisplay() {
        const timerElement = document.getElementById('timer');
        const progressElement = document.getElementById('timer-progress');
        
        if (timerElement) {
            timerElement.textContent = this.timeLeft;
        }
        
        if (progressElement) {
            const progressPercent = (this.timeLeft / this.duration) * 100;
            progressElement.style.width = progressPercent + '%';
            progressElement.style.transition = 'width 1s linear';
            
            // 色を変更（残り5秒で赤に）
            if (this.timeLeft <= 5) {
                progressElement.className = 'progress-bar bg-danger';
            } else if (this.timeLeft <= 10) {
                progressElement.className = 'progress-bar bg-warning';
            }
        }
    }
    
    getTimeSpent() {
        // 実際の経過時間を計算
        const currentTime = Date.now();
        const elapsed = Math.round((currentTime - this.startTime) / 1000);
        return Math.max(0, elapsed);  // 負の値にならないように
    }
}

// カウントダウン機能
class CountdownTimer {
    constructor(duration = 3, onComplete = null) {
        this.duration = duration;
        this.countdown = duration;
        this.onComplete = onComplete;
        this.interval = null;
    }
    
    start() {
        this.hideButton();
        this.showCountdown();
        
        // すぐに最初の表示を更新
        this.updateDisplay();
        
        this.interval = setInterval(() => {
            this.countdown--;
            if (this.countdown > 0) {
                this.updateDisplay();
            } else {
                this.stop();
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 1000);
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }
    
    hideButton() {
        const button = document.querySelector('button');
        if (button) {
            button.style.display = 'none';
        }
    }
    
    showCountdown() {
        const countdownDisplay = document.getElementById('countdown-display');
        if (countdownDisplay) {
            countdownDisplay.style.display = 'block';
        }
    }
    
    updateDisplay() {
        const countdownNumber = document.getElementById('countdown-number');
        if (countdownNumber) {
            countdownNumber.textContent = this.countdown;
        }
    }
}

// フォーム送信処理
function setupQuizForm() {
    const form = document.getElementById('answer-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // 入力値の検証を実行
            if (!validateInputs()) {
                console.log('フォーム送信時に入力値検証に失敗したため送信をキャンセル');
                e.preventDefault();
                
                // エラーメッセージを表示
                showErrorMessage('回答を入力してください。');
                return false;
            }
            
            // 次の問題に進むイベントを発火
            window.dispatchEvent(new Event('quizNextQuestion'));
            
            const timeSpentInput = document.getElementById('time-spent');
            if (timeSpentInput && window.quizTimer) {
                const timeSpent = window.quizTimer.getTimeSpent();
                timeSpentInput.value = timeSpent;
            }
        });
    }
}

// Enterキーでの送信（記述問題用）
function setupEnterKeySubmit() {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            const selectedChoiceInput = document.getElementById('selected_choice');
            
            // 選択問題の場合は選択肢のEnterキー処理に任せる
            if (selectedChoiceInput) {
                return;
            }
            
            // 記述問題の場合
            const textInputs = document.querySelectorAll('input[type="text"]');
            let hasInput = false;
            
            textInputs.forEach(input => {
                if (input.value.trim() !== '') {
                    hasInput = true;
                }
            });
            
            // 入力値がない場合は送信しない
            if (!hasInput) {
                console.log('入力値がないため送信をキャンセル');
                event.preventDefault();
                showErrorMessage('回答を入力してください。');
                return;
            }
            
            // 入力値の検証を実行
            if (!validateInputs()) {
                console.log('入力値検証に失敗したため送信をキャンセル');
                event.preventDefault();
                showErrorMessage('回答を入力してください。');
                return;
            }
            
            // 入力値がある場合は送信
            event.preventDefault();
            const form = document.getElementById('answer-form');
            if (form) {
                // 次の問題に進むイベントを発火
                window.dispatchEvent(new Event('quizNextQuestion'));
                
                const timeSpentInput = document.getElementById('time-spent');
                if (timeSpentInput && window.quizTimer) {
                    const timeSpent = window.quizTimer.getTimeSpent();
                    timeSpentInput.value = timeSpent;
                }
                form.submit();
            }
        }
    });
}

// 自動フォーカスと入力検証
function setupAutoFocusAndValidation() {
    const firstInput = document.querySelector('input[type="text"]');
    const submitBtn = document.getElementById('submit-btn');
    
    if (firstInput) {
        firstInput.focus();
        
        // 入力検証を追加
        firstInput.addEventListener('input', function() {
            validateInputs();
        });
    }
    
    // 複数入力欄がある場合の検証
    const allInputs = document.querySelectorAll('input[type="text"]');
    allInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateInputs();
        });
    });
}

// 入力値の検証
function validateInputs() {
    const submitBtn = document.getElementById('submit-btn');
    const selectedChoiceInput = document.getElementById('selected_choice');
    
    let isValid = false;
    
    if (selectedChoiceInput) {
        // 選択問題の場合
        if (selectedChoiceInput.value.trim() !== '') {
            isValid = true;
            submitBtn.disabled = false;
        } else {
            isValid = false;
            submitBtn.disabled = true;
        }
    } else {
        // 記述問題の場合（単一解答欄または複数解答欄）
        const textInputs = document.querySelectorAll('input[type="text"]');
        let hasInput = false;
        
        // 複数解答欄の場合、少なくとも1つの入力があれば有効
        textInputs.forEach(input => {
            if (input.value.trim() !== '') {
                hasInput = true;
            }
        });
        
        isValid = hasInput;
        submitBtn.disabled = !hasInput;
        
        console.log('記述問題の検証結果:', { hasInput, isValid, inputCount: textInputs.length });
    }
    
    return isValid;
}

// 選択肢のクリック機能
function setupChoiceSelection() {
    const choiceItems = document.querySelectorAll('.choice-item');
    const selectedChoiceInput = document.getElementById('selected_choice');
    const submitBtn = document.getElementById('submit-btn');
    
    choiceItems.forEach(item => {
        item.addEventListener('click', function() {
            // 他の選択肢の選択状態を解除
            choiceItems.forEach(choice => choice.classList.remove('selected'));
            
            // この選択肢を選択状態にする
            this.classList.add('selected');
            
            // 隠しフィールドに値を設定
            if (selectedChoiceInput) {
                selectedChoiceInput.value = this.getAttribute('data-value');
            }
            
            // 送信ボタンを有効化
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        });
    });
}

// Enterキーでの選択肢送信
function setupChoiceEnterKey() {
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            const selectedChoiceInput = document.getElementById('selected_choice');
            
            // 選択問題の場合のみ処理
            if (selectedChoiceInput) {
                // 入力値の検証を実行
                if (!validateInputs()) {
                    event.preventDefault();
                    return;
                }
                
                // 選択肢が選択されている場合のみ送信
                if (selectedChoiceInput.value && selectedChoiceInput.value.trim() !== '') {
                    event.preventDefault();
                    const form = document.getElementById('answer-form');
                    if (form) {
                        // 次の問題に進むイベントを発火
                        window.dispatchEvent(new Event('quizNextQuestion'));
                        
                        const timeSpentInput = document.getElementById('time-spent');
                        if (timeSpentInput && window.quizTimer) {
                            const timeSpent = window.quizTimer.getTimeSpent();
                            timeSpentInput.value = timeSpent;
                        }
                        form.submit();
                    }
                }
            }
        }
    });
}

// クイズ開始時の初期化
function initializeQuiz() {
    // タイマーを開始（既存のタイマー情報があれば継続）
    window.quizTimer = new QuizTimer(20);
    window.quizTimer.onTimeout = function() {
        const timeSpentInput = document.getElementById('time-spent');
        if (timeSpentInput) {
            const timeSpent = window.quizTimer.getTimeSpent();
            timeSpentInput.value = timeSpent;
        }
        const form = document.getElementById('answer-form');
        if (form) {
            form.submit();
        }
    };
    
    // クイズ終了時にタイマーをクリア
    window.addEventListener('beforeunload', function() {
        if (window.quizTimer) {
            window.quizTimer.stop();
        }
    });
    
    // 次の問題に進む時にタイマーをリセット
    window.addEventListener('quizNextQuestion', function() {
        if (window.quizTimer) {
            window.quizTimer.stop();
            sessionStorage.removeItem('quizTimer');
        }
    });
    
    window.quizTimer.start();
    
    // フォームとキーボードイベントを設定
    setupQuizForm();
    setupEnterKeySubmit();
    setupAutoFocusAndValidation();
    
    // 選択肢の機能を設定
    setupChoiceSelection();
    setupChoiceEnterKey();
    
    // 初期状態で送信ボタンを無効化
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
    }
}

// カウントダウン開始時の初期化
function initializeCountdown(onComplete) {
    const countdown = new CountdownTimer(3, onComplete);
    countdown.start();
}

// 吹き出し形式のエラーメッセージ表示機能
function showErrorMessage(message) {
    console.log('エラーメッセージを表示:', message);
    
    // 既存のエラーメッセージを削除
    const existingTooltip = document.querySelector('.error-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // 入力フィールドを取得
    let targetElement = null;
    const selectedChoiceInput = document.getElementById('selected_choice');
    
    if (selectedChoiceInput) {
        // 選択問題の場合、選択肢のコンテナを対象にする
        targetElement = document.querySelector('.choice-options');
    } else {
        // 記述問題の場合、最初の入力フィールドを対象にする
        targetElement = document.querySelector('input[type="text"]');
    }
    
    if (!targetElement) {
        console.log('ターゲット要素が見つかりません');
        return;
    }
    
    console.log('ターゲット要素:', targetElement);
    
    // 吹き出し要素を作成
    const tooltipDiv = document.createElement('div');
    tooltipDiv.className = 'error-tooltip';
    tooltipDiv.innerHTML = `
        <div class="tooltip-content">
            <div class="tooltip-arrow"></div>
            <div class="tooltip-text">${message}</div>
        </div>
    `;
    
    // 吹き出しを表示
    document.body.appendChild(tooltipDiv);
    
    // 位置を計算して配置
    const rect = targetElement.getBoundingClientRect();
    const tooltipRect = tooltipDiv.getBoundingClientRect();
    
    console.log('位置計算:', { rect, tooltipRect });
    
    // 吹き出しを入力フィールドの上に配置
    tooltipDiv.style.left = rect.left + (rect.width / 2) - (tooltipRect.width / 2) + 'px';
    tooltipDiv.style.top = rect.top - tooltipRect.height - 10 + 'px';
    
    console.log('吹き出し配置完了');
    
    // 3秒後に自動で消す
    setTimeout(() => {
        if (tooltipDiv.parentNode) {
            tooltipDiv.remove();
        }
    }, 3000);
}

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // クイズ問題ページの場合
    if (document.getElementById('timer')) {
        initializeQuiz();
    }
});
