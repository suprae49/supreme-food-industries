// Supreme Food Industry — bag weight calculator (Java)
public class RiceCalc {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("usage: RiceCalc <bags> [kg_per_bag=25]");
            System.exit(1);
        }
        long bags = Long.parseLong(args[0]);
        double kgEach = args.length >= 2 ? Double.parseDouble(args[1]) : 25.0;
        if (bags < 0 || kgEach <= 0) {
            System.err.println("invalid input");
            System.exit(1);
        }
        double total = bags * kgEach;
        System.out.printf(
            "{\"ok\":true,\"lang\":\"java\",\"bags\":%d,\"kg_per_bag\":%.2f,\"total_kg\":%.2f,\"total_quintal\":%.3f}%n",
            bags, kgEach, total, total / 100.0
        );
    }
}
