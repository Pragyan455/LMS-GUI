import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.sql.*;

public class LMS_Full {

   static JTextField fBook, fBranch, fCard, fDate, fDue;
    static JTextField bName, bAddress, bPhone;
    static JTextField fTitle, fAuthor, fStart, fEnd, fFilter;
    static JComboBox<String> publisherBox;

    public static void main(String[] args) {
      try {
            Class.forName("org.sqlite.JDBC");
            conn = DriverManager.getConnection("jdbc:sqlite:LMS.db");
            System.out.println("Connected!");
        } catch (Exception e) {
            e.printStackTrace();
        }


        JFrame frame = new JFrame("LMS System");
        frame.setSize(1000, 600);
        frame.setLayout(new BorderLayout());

        // TABLE
        model = new DefaultTableModel();
        table = new JTable(model);
        frame.add(new JScrollPane(table), BorderLayout.CENTER);
       
        // ---------------- FIELDS ----------------
        fBook = new JTextField(); 
        fBranch = new JTextField();
        fCard = new JTextField(); 
        fDate = new JTextField(); 
        fDue = new JTextField();

        bName = new JTextField(); 
        bAddress = new JTextField(); 
        bPhone = new JTextField();

        fTitle = new JTextField(); 
        fAuthor = new JTextField();
        fStart = new JTextField(); 
        fEnd = new JTextField(); 
        fFilter = new JTextField();

        publisherBox = new JComboBox<>();

        loadPublishers();

        // sizes
        Dimension dim = new Dimension(110, 25);
        JTextField[] fields = {fBook,fBranch,fCard,fDate,fDue,bName,bAddress,bPhone,fTitle,fAuthor,fStart,fEnd,fFilter};
        for (JTextField f : fields) f.setPreferredSize(dim);

        publisherBox.setPreferredSize(new Dimension(140,25));


        // ---------------- DROPDOWN ----------------
        JComboBox<String> publisherBox = new JComboBox<>();

        try {
            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery("SELECT publisher_name FROM PUBLISHER");

            while (rs.next()) {
                publisherBox.addItem(rs.getString("publisher_name"));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

       


        // ----------- MAIN PANEL -----------
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));

        // ----------- ROW 1 -----------
        JPanel row1 = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 10));

        row1.add(new JLabel("Book ID")); row1.add(fBook);
        row1.add(new JLabel("Branch ID")); row1.add(fBranch);
        row1.add(new JLabel("Card No")); row1.add(fCard);
        row1.add(new JLabel("Date Out")); row1.add(fDate);
        row1.add(new JLabel("Due Date")); row1.add(fDue);

        // ----------- ROW 2 -----------
        JPanel row2 = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 10));

        row2.add(new JLabel("Borrower Name")); row2.add(bName);
        row2.add(new JLabel("Borrower Address")); row2.add(bAddress);
        row2.add(new JLabel("Borrower Phone")); row2.add(bPhone);

        // ----------- ROW 3 -----------
        JPanel row3 = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 10));

        row3.add(new JLabel("Book Title")); row3.add(fTitle);
        row3.add(new JLabel("Author")); row3.add(fAuthor);
        row3.add(new JLabel("Publisher")); row3.add(publisherBox);

        // ----------- ROW 4 -----------
        JPanel row4 = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 10));

        row4.add(new JLabel("Start Date")); row4.add(fStart);
        row4.add(new JLabel("End Date")); row4.add(fEnd);
        row4.add(new JLabel("Filter Name")); row4.add(fFilter);

        // ----------- ADD ROWS -----------
        panel.add(row1);
        panel.add(row2);
        panel.add(row3);
        panel.add(row4);

        frame.add(panel, BorderLayout.NORTH);
        
        // ---------------- BUTTONS ----------------

        JPanel buttons = new JPanel();

        JButton checkout = new JButton("Checkout");
        JButton addBorrower = new JButton("Add Borrower");
        JButton addBook = new JButton("Add Book");
        JButton copies = new JButton("Copies/Branch");
        JButton late = new JButton("Late Books");
        JButton fees = new JButton("Borrower Fees");
        JButton info = new JButton("Book Info");

        buttons.add(checkout);
        buttons.add(addBorrower);
        buttons.add(addBook);
        buttons.add(copies);
        buttons.add(late);
        buttons.add(fees);
        buttons.add(info);

        frame.add(buttons, BorderLayout.SOUTH);

        // ---------------- CHECKOUT ----------------
        checkout.addActionListener(e -> {
            try {
                PreparedStatement ps = conn.prepareStatement(
                        "INSERT INTO BOOK_LOANS (book_id, branch_id, card_no, date_out, due_date) VALUES (?, ?, ?, ?, ?)");
                ps.setInt(1, Integer.parseInt(fBook.getText()));
                ps.setInt(2, Integer.parseInt(fBranch.getText()));
                ps.setInt(3, Integer.parseInt(fCard.getText()));
                ps.setString(4, fDate.getText());
                ps.setString(5, fDue.getText());
                ps.executeUpdate();

                showQuery("SELECT * FROM BOOK_COPIES WHERE book_id="+fBook.getText()+" AND branch_id="+fBranch.getText());

            } catch (Exception ex) {
                showError(ex);
            }
        });

        // ---------------- ADD BORROWER ----------------
        addBorrower.addActionListener(e -> {
            try {
                PreparedStatement ps = conn.prepareStatement(
                        "INSERT INTO BORROWER (name) VALUES (?)",
                        Statement.RETURN_GENERATED_KEYS);
                ps.setString(1, bName.getText());
                ps.setString(2, bAddress.getText());
                ps.setInt(3, Integer.parseInt(bPhone.getText()));
                ps.executeUpdate();

                ResultSet rs = ps.getGeneratedKeys();
                if (rs.next()) {
                    JOptionPane.showMessageDialog(frame, "Card No: " + rs.getInt(1));
                }

            } catch (Exception ex) {
                showError(ex);
            }
        });

        // ---------------- ADD BOOK ----------------
        addBook.addActionListener(e -> {
    try {
        String title = fTitle.getText();
        String publisher = (String) publisherBox.getSelectedItem();
        String author = fAuthor.getText();

        // Insert into BOOK
        PreparedStatement ps = conn.prepareStatement(
            "INSERT INTO BOOK (title, book_publisher) VALUES (?, ?)",
            Statement.RETURN_GENERATED_KEYS
        );
        ps.setString(1, title);
        ps.setString(2, publisher);
        ps.executeUpdate();

        // Get book_id
        ResultSet rs = ps.getGeneratedKeys();
        int book_id = 0;
        if (rs.next()) book_id = rs.getInt(1);

        // Insert author
        PreparedStatement pa = conn.prepareStatement(
            "INSERT INTO BOOK_AUTHORS (book_id, author_name) VALUES (?, ?)"
        );
        pa.setInt(1, book_id);
        pa.setString(2, author);
        pa.executeUpdate();

        // Add to all branches
        Statement st = conn.createStatement();
        ResultSet br = st.executeQuery("SELECT branch_id FROM LIBRARY_BRANCH");

        while (br.next()) {
            PreparedStatement pc = conn.prepareStatement(
                "INSERT INTO BOOK_COPIES (book_id, branch_id, no_of_copies) VALUES (?, ?, 5)"
            );
            pc.setInt(1, book_id);
            pc.setInt(2, br.getInt("branch_id"));
            pc.executeUpdate();
        }

        JOptionPane.showMessageDialog(frame, "Book added successfully!");

    } catch (Exception ex) {
        showError(ex);
    }
});

        // ---------------- COPIES PER BRANCH ----------------
        copies.addActionListener(e -> {
            showQuery(
                    "SELECT LB.branch_name, COUNT(*) FROM BOOK_LOANS L " +
                    "JOIN BOOK B ON L.book_id=B.book_id " +
                    "JOIN LIBRARY_BRANCH LB ON L.branch_id=LB.branch_id " +
                    "WHERE B.title LIKE '%"+fTitle.getText()+"%' GROUP BY LB.branch_name"
            );
        });

        // ---------------- LATE BOOKS ----------------
        late.addActionListener(e -> {
            showQuery(
                    "SELECT book_id, JULIANDAY(Returned_date)-JULIANDAY(due_date) " +
                    "FROM BOOK_LOANS WHERE Returned_date > due_date " +
                    "AND due_date BETWEEN '"+fStart.getText()+"' AND '"+fEnd.getText()+"'"
            );
        });

        // ---------------- BORROWER FEES ----------------
        fees.addActionListener(e -> {
            showQuery(
                    "SELECT card_no, borrower_name, " +
                    "'$' || printf('%.2f', COALESCE(SUM(LateFeeBalance),0)) " +
                    "FROM vBookLoanInfo WHERE borrower_name LIKE '%"+fFilter.getText()+"%' " +
                    "GROUP BY card_no ORDER BY SUM(LateFeeBalance) DESC"
            );
        });

        // ---------------- BOOK INFO ----------------
        info.addActionListener(e -> {
            showQuery(
                    "SELECT title, CASE WHEN LateFeeBalance IS NULL THEN 'Non-Applicable' " +
                    "ELSE '$' || printf('%.2f', LateFeeBalance) END " +
                    "FROM vBookLoanInfo WHERE card_no="+fCard.getText()
            );
        });

        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }

    // ---------------- HELPER FUNCTIONS ----------------
    static void showQuery(String sql) {
        try {
            model.setRowCount(0);
            model.setColumnCount(0);

            Statement st = conn.createStatement();
            ResultSet rs = st.executeQuery(sql);

            int cols = rs.getMetaData().getColumnCount();

            for (int i = 1; i <= cols; i++) {
                model.addColumn(rs.getMetaData().getColumnName(i));
            }

            while (rs.next()) {
                Object[] row = new Object[cols];
                for (int i = 0; i < cols; i++) {
                    row[i] = rs.getObject(i+1);
                }
                model.addRow(row);
            }

        } catch (Exception e) {
            showError(e);
        }
    }

    static void showError(Exception e) {
        JOptionPane.showMessageDialog(null, e.getMessage());
    }
}