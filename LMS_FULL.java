import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.sql.*;

public class LMS_Full {

    static Connection conn;
    static JTable table;
    static DefaultTableModel model;

    public static void main(String[] args) {
      try {
    Class.forName("org.sqlite.JDBC");

    conn = DriverManager.getConnection(
        "jdbc:sqlite:/Users/pragyanbhattarai/UTA/CSE 3330/GUi/LMS.db"
    );

    System.out.println("Connection = " + conn);

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

        JPanel panel = new JPanel(new GridLayout(3,4,5,5));

        JTextField fBook = new JTextField();
        JTextField fBranch = new JTextField();
        JTextField fCard = new JTextField();
        JTextField fDate = new JTextField();
        JTextField fDue = new JTextField();
        JTextField fName = new JTextField();
        JTextField fTitle = new JTextField();
        JTextField fStart = new JTextField();
        JTextField fEnd = new JTextField();
        JTextField fFilter = new JTextField();

        panel.add(new JLabel("Book ID")); panel.add(fBook);
        panel.add(new JLabel("Branch ID")); panel.add(fBranch);
        panel.add(new JLabel("Card No")); panel.add(fCard);
        panel.add(new JLabel("Date Out")); panel.add(fDate);
        panel.add(new JLabel("Due Date")); panel.add(fDue);
        panel.add(new JLabel("Name")); panel.add(fName);
        panel.add(new JLabel("Book Title")); panel.add(fTitle);
        panel.add(new JLabel("Start Date")); panel.add(fStart);
        panel.add(new JLabel("End Date")); panel.add(fEnd);
        panel.add(new JLabel("Filter Name")); panel.add(fFilter);

        frame.add(panel, BorderLayout.NORTH);

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
                ps.setString(1, fName.getText());
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
                PreparedStatement ps = conn.prepareStatement(
                        "INSERT INTO BOOK (title, book_publisher) VALUES (?, 'DefaultPub')",
                        Statement.RETURN_GENERATED_KEYS);
                ps.setString(1, fTitle.getText());
                ps.executeUpdate();

                ResultSet rs = ps.getGeneratedKeys();
                int book_id = 0;
                if (rs.next()) book_id = rs.getInt(1);

                PreparedStatement pa = conn.prepareStatement(
                        "INSERT INTO BOOK_AUTHORS VALUES (?, 'Unknown')");
                pa.setInt(1, book_id);
                pa.executeUpdate();

                Statement st = conn.createStatement();
                ResultSet br = st.executeQuery("SELECT branch_id FROM LIBRARY_BRANCH");

                while (br.next()) {
                    PreparedStatement pc = conn.prepareStatement(
                            "INSERT INTO BOOK_COPIES VALUES (?, ?, 5)");
                    pc.setInt(1, book_id);
                    pc.setInt(2, br.getInt(1));
                    pc.executeUpdate();
                }

                JOptionPane.showMessageDialog(frame, "Book added to all branches!");

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