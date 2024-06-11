# Academic-Data-Hashing-Project

- SOURCES:
preprocess.py -> Το αρχείο αυτό ως command-line argument παίρνει ένα αρχείο δεδομένων <name>.csv και παράγει από αυτό τα λεξικάuserList, movieMap και movieList τα οποία γίνονται export σε csv και αποθηκεύονται στον φάκελο EXPERIMENTS. Γι αυτό το λόγο, το preprocess.py πρέπει να εκτελεστεί πρώτο ώστε να είναι διαθέσιμα τα λεξικά σε csv για ναχρησιμοποιηθούνε μετέπειτα.

main.py -> Το αρχείο αυτό περιέχει τη βασική λειτουργικότητα του προγράμματος.Ως command-line arguments παίρνει ένα αρχείο δεδομένων <name>.csv, τοκατώφλι s, τον αριθμό x των πρώτων ταινιών που θα συγκριθούν και μία παράμετρο <i> η οποία για τιμή 1 δημιουργεί ένα καινούριο μητρώο υπογραφών SIG, ενώ για τιμή 0 χρησιμοποιεί το ήδη υπάρχον.

universalHashFunctions.py 

- EXPERIMENTS:
     Παραχθέντα csv αρχεία με τα λεξικά userList, movieMap και movieListκαι τα μητρώα SIG για τα αρχεία δεδομένων ratings_100users.csv καιratings.csv
    Screenshots από την εκτέλεση της πειραματικής αξιολόγησης
    Εικόνες με τις .γραφικές παραστάσεις των false-pos, false-neg και PRECISION, RECALL, F1 metrics


