using System.Net.Sockets;
using System.Xml;
using System.Text;

String deviceIpAddress = "10.0.0.20";
Int32  devicePort      = 4000;

Int32 acknowledge_count = 6;

Dictionary<String, String> axes = new()
{
  { "x",       "1" },
  { "y",       "2" },
  { "z",       "3" },
  { "pol",     "4" },
  { "slide",   "5" },
  { "azimuth", "6" },
};

Dictionary<String, String> axesSafeAcceleration = new()
{
  { "x",       "0.05" },
  { "y",       "0.1"  },
  { "z",       "0.1"  },
  { "pol",     "10"   },
  { "slide",   "0.01" },
  { "azimuth", "1"    },
};

Dictionary<String, String> axesSafeSpeed = new()
{
  { "x",        "0.1"  },
  { "y",        "0.2"  },
  { "z",        "0.02" },
  { "pol",      "10"   },
  { "slide",    "0.01" },
  { "azimuth",  "1"    },
};

try
{
	// Prefer a using declaration to ensure the instance is Disposed later.
	TcpClient deviceClient = new(deviceIpAddress, devicePort);

	// Get a client stream for reading and writing.
	NetworkStream net_stream = deviceClient.GetStream();
  // deviceClient.ReceiveTimeout = 1000;

	var builder = WebApplication.CreateBuilder(args);
  builder.Logging.AddJsonConsole();
  var app = builder.Build();

  app.MapPut("/move/{move_type}/{axis}/{position}", (String axis, String move_type, String position) =>
  {
    if (!axes.TryGetValue(axis, out string? value))
    {
      return Results.Json("{ 'error': 'Axis not found'}", contentType: "application/json");
    }

    if (move_type == "relative")
    {
      move_to(net_stream, axis, get_position(net_stream, axis)+Convert.ToDouble(position));
    }
    else 
    {
      move_to(net_stream, axis, Convert.ToDouble(position));
    }
    return Results.Json("{}", contentType: "application/json");
  });

  app.MapPut("/reference/{axis}/{position}", (String axis, String position) =>
  {
    if (!axes.TryGetValue(axis, out string? value))
    {
      return Results.Json("{ 'error': 'Axis not found'}", contentType: "application/json");
    }
    set_reference(net_stream, axis, Convert.ToDouble(position));
    return Results.Json("{}", contentType: "application/json");
  });

  
  app.MapPut("/home/{axis}", (String axis) =>
  {
    if (!axes.TryGetValue(axis, out string? value))
    {
      return Results.Json("{ 'error': 'Axis not found'}", contentType: "application/json");
    }
    home(net_stream, axis);
    return Results.Json("{}", contentType: "application/json");
  });
  
  app.MapPut("/quick_stop", () =>
  {
    quick_stop(net_stream, "x");
    quick_stop(net_stream, "y");
    quick_stop(net_stream, "z");
    quick_stop(net_stream, "pol");
    quick_stop(net_stream, "slide");
    quick_stop(net_stream, "azimuth");
    return Results.Json("{}", contentType: "application/json");
  });

  app.MapPut("/quick_stop/{axis}", (String axis) =>
  {
    if (!axes.TryGetValue(axis, out string? value))
    {
      return Results.Json("{ 'error': 'Axis not found'}", contentType: "application/json");
    }
    quick_stop(net_stream, axis);
    return Results.Json("{}", contentType: "application/json");
  });
  
  app.MapPut("/bringxy", () =>
  {
    move_to(net_stream, "x", get_lower_limit(net_stream, "x"));
    move_to(net_stream, "y", get_lower_limit(net_stream, "y")+0.5);
    return Results.Json("{}", contentType: "application/json");
  });

	app.MapDelete("/", () => "Hello World!");

	app.Run();
}
catch (ArgumentNullException e)
{
	Console.WriteLine("ArgumentNullException: {0}", e);
}
catch (SocketException e)
{
	Console.WriteLine("SocketException: {0}", e);
}

Double get_position(NetworkStream net_stream, String axis)
{
	for (int i = 0; i < acknowledge_count; i++)
	{
		acknowledge(net_stream);
	}

	XmlDocument doc = new XmlDocument();
  XmlElement  state;
  XmlElement  section;
  XmlElement  query;
  XmlNode     entry;

  Byte[] buffer = new Byte[1024];
  int bytes_received = 0;
  String read_data = new("");

  state   = doc.CreateElement("par");
  section = doc.CreateElement("section");
  query   = doc.CreateElement("query");
  query.SetAttribute("name", "Position");
  section.SetAttribute("name", "Axis "+axes[axis]);
  section.AppendChild(query);
  state.AppendChild(section);
  doc.AppendChild(state);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));

  bytes_received = net_stream.Read(buffer);
  read_data      = Encoding.UTF8.GetString(buffer.AsSpan(0, bytes_received));

  doc.RemoveAll();
  doc.LoadXml(read_data);
  entry = doc.SelectSingleNode("//par//section//entry") ?? doc.CreateElement("error");
  try
  {
#pragma warning disable CS8602 // Dereference of a possibly null reference.
    return Convert.ToDouble(entry.Attributes["v1"].InnerText.Substring(0, Math.Min(entry.Attributes["v1"].InnerText.Length,entry.Attributes["v1"].InnerText.IndexOf('.') + 5)));
#pragma warning restore CS8602 // Dereference of a possibly null reference.
  }
  catch (System.NullReferenceException e)
  {
    Console.WriteLine("ArgumentNullException: {0}", e.ToString());
    return 0;
  }
}

void move_to(NetworkStream net_stream, String axis, Double position)
{
	for (int i = 0; i < acknowledge_count; i++)
	{
		acknowledge(net_stream);
	}

	XmlDocument doc = new XmlDocument();
  XmlElement  el  = doc.CreateElement("command");

  el.SetAttribute("name", "MoveAbs");
  el.SetAttribute("axis", axes[axis]);
  el.SetAttribute("Acceleration", axesSafeAcceleration[axis]);
  el.SetAttribute("Deceleration", axesSafeAcceleration[axis]);
  el.SetAttribute("Velocity", axesSafeSpeed[axis]);
  el.SetAttribute("Direction", "Auto");
  el.SetAttribute("Position", position.ToString());
  doc.AppendChild(el);
  try
  {
    net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));
  }
  catch (System.NullReferenceException e)
  {
    Console.WriteLine("ArgumentNullException: {0}", e.ToString());
  }
}

Double get_lower_limit(NetworkStream net_stream, String axis)
{
  for (int i = 0; i<acknowledge_count; i++)
  {
		acknowledge(net_stream);
	}

  XmlDocument doc = new XmlDocument();
  XmlElement  state;
  XmlElement  section;
  XmlElement  query;
  XmlNode     entry;

  Byte[] buffer = new Byte[1024];
  int bytes_received = 0;
  String read_data = new("");

  state   = doc.CreateElement("par");
  section = doc.CreateElement("section");
  query   = doc.CreateElement("query");
  query.SetAttribute("name", "Position");
  section.SetAttribute("name", "Axis "+axes[axis]);
  section.AppendChild(query);
  state.AppendChild(section);
  doc.AppendChild(state);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));

  bytes_received = net_stream.Read(buffer);
  read_data      = Encoding.UTF8.GetString(buffer.AsSpan(0, bytes_received));

  doc.RemoveAll();
  doc.LoadXml(read_data);
  entry = doc.SelectSingleNode("//par//section//entry") ?? doc.CreateElement("error");
  try
  {
#pragma warning disable CS8602 // Dereference of a possibly null reference.
    return Convert.ToDouble(entry.Attributes?["min"]?.InnerText[..(entry.Attributes["min"].InnerText.IndexOf('.') + 5)]);
#pragma warning restore CS8602 // Dereference of a possibly null reference.
  }
  catch (System.NullReferenceException e)
  {
    Console.WriteLine("ArgumentNullException: {0}", e.ToString());
    return 0;
  }
}

void quick_stop(NetworkStream net_stream, String axis) {
	for (int i = 0; i < acknowledge_count; i++)
	{
		acknowledge(net_stream);
	}

  XmlDocument doc = new XmlDocument();
  XmlElement  el  = doc.CreateElement("command");
  el.SetAttribute("name", "QuickStop");
  el.SetAttribute("axis", "Axis " + axes[axis]);
  doc.AppendChild(el);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));
}

void home(NetworkStream net_stream, String axis) {
	for (int i = 0; i < acknowledge_count; i++)
	{
		acknowledge(net_stream);
	}

  XmlDocument doc = new XmlDocument();
  XmlElement  el  = doc.CreateElement("command");
  el.SetAttribute("name", "Reference");
  el.SetAttribute("axis", "Axis " + axes[axis]);
  doc.AppendChild(el);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));
}

void set_reference(NetworkStream net_stream, String axis, Double offset) {
	for (int i = 0; i < acknowledge_count; i++)
	{
		acknowledge(net_stream);
	}

	XmlDocument doc = new XmlDocument();
  XmlElement el   = doc.CreateElement("command");
  el.SetAttribute("name", "Reference");
  el.SetAttribute("axis", "Axis " + axes[axis]);
  el.SetAttribute("NewPosition", offset.ToString());
  doc.AppendChild(el);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));
}

void acknowledge(NetworkStream net_stream) {
  XmlDocument doc = new XmlDocument();
  XmlElement  el  = doc.CreateElement("command");
  el.SetAttribute("name", "Ack");
  doc.AppendChild(el);
  net_stream.Write(Encoding.ASCII.GetBytes(doc.OuterXml.ToString()));
}